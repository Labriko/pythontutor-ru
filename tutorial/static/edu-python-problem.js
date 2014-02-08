/*

Online Python Tutor
https://github.com/pgbovine/OnlinePythonTutor/

Copyright (C) 2010-2012 Philip J. Guo (philip@pgbovine.net)

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/

// UI for online problems

// Pre-req: edu-python.js and jquery.ba-bbq.min.js should be imported BEFORE this file

var SERVER_PREFIX = '/'

var problemUrlname = location.pathname.replace(/(.+problems\/)([^\/]+)(\/.*)/, '$2');

// parsed form of a problem file from
var curProblem = null;


// matching arrays of test code and 'expected outputs' from those tests
var tests = null;
var answers = null;
var curTestIndex = -1;

// the results returned by executing the respective 'tests' and 'answers'
// Python code.  See resetTestResults for invariants.
var testResults = null;

// Pre: 'tests' and 'answers' are non-null
function resetTestResults() {
  testResults = [];
  $.each(tests, function(i) {
    testResults.push(null);
  });

  assert(testResults.length > 0);
  assert(testResults.length == tests.length);
}


$(document).ready(function() {
  eduPythonCommonInit(); // must call this first!

  registerInputTextarea('actualCodeInput');

  // this doesn't work since we need jquery.textarea.js ...
  //$("#actualCodeInput").tabby(); // recognize TAB and SHIFT-TAB
  //$("#testCodeInput").tabby();   // recognize TAB and SHIFT-TAB


  // be friendly to the browser's forward and back buttons
  // thanks to http://benalman.com/projects/jquery-bbq-plugin/
  $(window).bind("hashchange", function(e) {
    appMode = $.bbq.getState("mode"); // assign this to the GLOBAL appMode

    // default mode is 'edit'
    if (appMode == undefined) {
      appMode = 'edit';
    }

    // if there's no curTrace, then default to edit mode since there's
    // nothing to visualize or grade:
    if (!curTrace) {
      appMode = 'edit';
      $.bbq.pushState({ mode: 'edit' });
    }


    if (appMode == 'edit') {
      $("#pyInputPane").show();
      $("#pyOutputPane").hide();
      $("#pyGradingPane").hide();
    }
    else if (appMode == 'visualize') {
      $("#pyInputPane").hide();
      $("#pyOutputPane").show();
      $("#pyGradingPane").hide();

      window.scrollTo(0, 0);

      $('#submitBtn').html("Отправить решение");
      $('#submitBtn').attr('disabled', false);

      $('#executeBtn').html("Запустить программу");
      $('#executeBtn').attr('disabled', false);


      // do this AFTER making #pyOutputPane visible, or else
      // jsPlumb connectors won't render properly
      processTrace(curTrace /* kinda dumb and redundant */, true);

      // don't let the user submit answer when there's an error
      var hasError = false;
      for (var i = 0; i < curTrace.length; i++) {
         var curEntry = curTrace[i];
         if (curEntry.event == 'exception' ||
             curEntry.event == 'uncaught_exception') {
           hasError = true;
           break;
         }
      }
      $('#submitBtn').attr('disabled', hasError);
    }
    else if (appMode == 'grade') {
      $("#gradeMatrix #gradeMatrixTbody").empty(); // clear it!!!

      $("#pyInputPane").hide();
      $("#pyOutputPane").hide();
      $("#pyGradingPane").show();

      gradeSubmission();
    }
  });


  // From: http://benalman.com/projects/jquery-bbq-plugin/
  //   Since the event is only triggered when the hash changes, we need
  //   to trigger the event now, to handle the hash the page may have
  //   loaded with.
  $(window).trigger( "hashchange" );


  // load the problem urlname specified by the query string
  
  $.get(SERVER_PREFIX + "load_problem/",
        {problem_urlname : problemUrlname},
        function(problemDat) {
          finishProblemInit(problemDat);
        },
        "json");

});


function enterEditMode() {
  $.bbq.pushState({ mode: 'edit' });
}

function enterVisualizeMode(traceData) {
  curTrace = traceData; // first assign it to the global curTrace, then
                        // let jQuery BBQ take care of the rest
  $.bbq.pushState({ mode: 'visualize' });
  $('#inputDataOnVisualizing').val($('#inputData').val());
}

function enterGradingMode() {
  $.bbq.pushState({ mode: 'grade' });
}


// returns a closure!
function genTestResultHandler(idx) {
  function ret(res) {
    assert(testResults[idx] === null);
    testResults[idx] = res;

    // if ALL results have been successfully delivered, then call
    // enterGradingMode() (remember that each result comes in
    // asynchronously and probably out-of-order)

    for (var i = 0; i < testResults.length; i++) {
      if (testResults[i] === null) {
        return;
      }
    }

    enterGradingMode();
  }

  return ret;
}

function genDebugLinkHandler(failingTestIndex) {
  function ret() {
    // Switch back to visualize mode, populating the "testCodeInput"
    // field with the failing test case, and RE-RUN the back-end to
    // visualize execution (this time with proper object IDs)
    curTestIndex = failingTestIndex;
    $("#inputData").val(tests[curTestIndex]);
    $("#inputDataOnVisualizing").val(tests[curTestIndex]);

    // prevent multiple-clicking ...
    $(this).html("Подождите...");
    $(this).attr('disabled', true);

    $("#executeBtn").trigger('click'); // emulate an execute button press!
  }

  return ret;
}


function finishProblemInit(problemDat) {
  curProblem = problemDat; // initialize global

  $("#ProblemName").html(problemDat.name);
  $("#ProblemStatement").html(problemDat.statement);

  // set some globals
  tests = problemDat.tests;
  answers = problemDat.answers;
  curTestIndex = 0;

  resetTestResults();


  $("#inputData").val(tests[0]);

  $("#actualCodeInput").val(problemDat.savedCode);


  $("#executeBtn").attr('disabled', false);
  $("#executeBtn").click(function() {
    $('#executeBtn').html("Ваша программа выполняется...");
    $('#executeBtn').attr('disabled', true);
    $("#pyOutputPane").hide();

    var submittedCode = $("#actualCodeInput").val();

    var postParams = {user_script : submittedCode};

    /*
    if (questionsDat.max_instructions) {
      postParams.max_instructions = questionsDat.max_instructions;
    }*/

    $.post(SERVER_PREFIX + "execute/",
       {user_script : $("#actualCodeInput").val(),
        input_data  : $("#inputData").val()},
       function(traceData) {
         renderPyCodeOutput(submittedCode);
         enterVisualizeMode(traceData);
       },
       "json");
  });


  $("#editBtn").click(function() {
    enterEditMode();
  });


  $("#submitBtn").click(function() {
    $('#submitBtn').html("Решение отправляется на проверку...");
    $('#submitBtn').attr('disabled', true);

    resetTestResults(); // prepare for a new fresh set of test results

    // remember that these results come in asynchronously and probably
    // out-of-order, so code very carefully here!!!
    for (var i = 0; i < tests.length; i++) {
      var submittedCode = $("#actualCodeInput").val();

      var postParams = {user_script : submittedCode, 
                        test_input  : tests[i],
                        test_answer : answers[i]};

      /*if (questionsDat.max_instructions) {
        postParams.max_instructions = questionsDat.max_instructions;
      }*/

      $.post(SERVER_PREFIX + "run_test/",
             postParams,
             genTestResultHandler(i),
             "json");
    }
  });
}


// should be called after ALL elements in testsTraces and answersTraces
// have been populated by their respective AJAX POST calls
function gradeSubmission() {
  $("#submittedCodePRE").html(htmlspecialchars($("#actualCodeInput").val()));

  for (var i = 0; i < tests.length; i++) {
    var res = testResults[i];

    $("#gradeMatrix tbody#gradeMatrixTbody").append('<tr class="gradeMatrixRow"></tr>');

    $("#gradeMatrix tr.gradeMatrixRow:last").append('<td class="testInputCell"><pre>' + tests[i] + '</pre></td>');

    // input_val could be null if there's a REALLY bad error :(
    // WHAT THE HELL IS IT?
    
    if (res.status == 'error') {
      $("#gradeMatrix tr.gradeMatrixRow:last").append('<td class="testOutputCell"><span style="color: ' + darkRed + '"><pre>' + res.test_val + '</pre></span></td>');
    }
    else {
      assert(res.status == 'ok');

      $("#gradeMatrix tr.gradeMatrixRow:last").append('<td class="testOutputCell"><pre>' + res.test_val + '</pre></td>');
    }

    $("#gradeMatrix tr.gradeMatrixRow:last").append('<td class="testAnswerCell"><pre>' + res.expect_val + '</pre></td>');

    if (res.passed_test) {
      var happyFaceImg = '<img style="vertical-align: middle;" src="' + SERVER_PREFIX + 'static/green-smile-face.png"/>';
      $("#gradeMatrix tr.gradeMatrixRow:last").append('<td class="statusCell">' + happyFaceImg + '</td>');

      // add an empty 'expected' cell
      // $("#gradeMatrix tr.gradeMatrixRow:last").append('<td class="expectedCell"></td>');
    }
    else {
      var sadFaceImg = '<img style="vertical-align: middle; margin-right: 8px;" src="' + SERVER_PREFIX + 'static/red-sad-face.jpg"/>';

      var debugBtnID  = 'debug_test_' + i;
      var debugMeBtn = '<button id="' + debugBtnID + '" class="debugBtn" type="button">Отладить на этом тесте</button>';
      // var expectedTd = '<td class="expectedCell">Expected: </td>';

      $("#gradeMatrix tr.gradeMatrixRow:last").append('<td class="statusCell">' + sadFaceImg + debugMeBtn + '</td>');

      // renderData(res.answer_val,
      //            $("#gradeMatrix tr.gradeMatrixRow:last td.expectedCell:last"),
      //            true /* ignoreIDs */);


      $('#' + debugBtnID).unbind(); // unbind it just to be paranoid
      $('#' + debugBtnID).click(genDebugLinkHandler(i));
    }
  }


  var numPassed = 0;
  for (var i = 0; i < tests.length; i++) {
    var res = testResults[i];
    if (res.passed_test) {
      numPassed++;
    }
  }

  if (numPassed < tests.length) {
    $("#gradeSummary").html('<span class="errorBackground">Ваше решение прошло ' + numPassed + ' тестов из ' + tests.length + '.  Попробуйте отладить свою программу!</span>');
  }
  else {
    assert(numPassed == tests.length);
    $("#gradeSummary").html('<span class="okBackground">Поздравляем, ваш код успешно прошел все тесты!</span>');

    // at this point we can tell the server that a problem has been solved
  }

  $.post(SERVER_PREFIX + "tutorial/post_grading_result/",
       {
        problem : problemUrlname,
        code    : $("#actualCodeInput").val(),
        result  : ((numPassed == tests.length) ? "ok" : "error"),
       });
}
