var SERVER_PREFIX = '/'

var lessons_comma_separated_list = location.pathname.replace(/(.+for_lessons\/)([^\/]+)(\/.*)/, '$2');

var lessons = [];

$(document).ready(function() {
    $.get(SERVER_PREFIX + "teacher_statistics/submissions/init_lessons_info/",
        {lessons_comma_separated_list : lessons_comma_separated_list},
        function(lessonsInfo) {
          initLessonsInfo(lessonsInfo);
        },
        "json");
})

function initLessonsInfo(lessonsInfo) {
    lessons = lessonsInfo;

    for (var i = 0; i < lessons.length; ++i) {
        $("#submissionsLessonsList").append(
            "<div class='submissionsLessonsListElement'>" + lessons[i].title + "</div>"
        );
        lessons.last_retrieved_submission = -1;
    }
}

function updateSubmissions() {
    for (var i = 0; i < lessons.length; ++i) {
        $.get(SERVER_PREFIX + "teacher_statistics/submissions/get_new_submissions/",
        {lesson_urlname: lessons[i].urlname,
         last_retrieved_submission: lessons[i].last_retrieved_submission},
        function(newSubmissions) {

        },
        "json");
    }
}
