#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <string.h>
#include <math.h>
#include <queue>
#include <stack>
#include <set>
#include <map>
#include <string>
#include <algorithm>
using namespace std;

const int inf = 1000*1000*1000;
#define CL(x,a) memset(x,a,sizeof(x));
#define ALL(v) (v).begin(),(v).end()
typedef long long LL;
int n,m;
vector< vector<double> > g,mat;
map<pair<int,int>,int> mp;

inline int tokID (int a,int b)
{
	if (mp[make_pair(a,b)] == 0)
		mp[make_pair(a,b)] = mp.size();
	return mp[make_pair(a,b)] - 1 + n;
}
inline void addCable(int a, int b, double r)
{
	vector<double> v(n+m+1,0);
	v[a] = 1;
	v[b] = -1;
	v[tokID(a,b)] = -r;
	mat.push_back(v);
}
void Init()
{
	vector<double> v(n+m+1);
	v[0] = 1;
	v[v.size()-1] = 1;
	mat.push_back(v);
	v.assign(n+m+1,0);
	v[n-1] = 1;
	mat.push_back(v);
	for (int i=0;i<n;i++)
	{
		vector<double> v;
		v.resize(n+m+1);
		bool flag = 0;
		for (int j=0;j<n;j++)
		{
			if (i==j || g[i][j] == 0)
				continue;
			if (i < j)
				addCable(i,j,g[i][j]);
			if (i == 0 || i == n-1)
				continue;
			flag = 1;
			if (j<i)
				v[tokID(j,i)]=1;
			else
				v[tokID(i,j)]=-1;
		}
		if (flag)
			mat.push_back(v);
	}
}
void sub(vector<double> &a, vector<double> &b, double k,int pos)
{
	for (int i=pos;i<n+m+1;i++)
	{
		a[i]-=b[i]*k;
	}
}
void findNotNull(int pos)
{
	int i;
	for (i=pos;i<n+m;i++)
	{
		if (mat[i][pos] != 0)
			break;
	}
	swap(mat[pos],mat[i]);
}
int pRes=0,qRes=1;
double dest = 1e+9;
void relax(double x, int p, int q)
{
	double t = (p+0.0)/q;
	if (fabs(t-x) < dest)
	{
		dest = fabs(t-x);
		pRes = p;
		qRes = q;
	}
}
int main()
{
	scanf("%d%d",&n,&m);
	int S=0;
	g.resize(n,vector<double>(n,0));
	for (int i=0;i<m;i++)
	{
		int a,b;
		double r;
		scanf("%d%d%lf",&a,&b,&r);
		a--;b--;
		if (g[a][b] != 0)
		{
			r = 1/(1/r+1/g[a][b]);
			++S;
		}
		g[a][b] = g[b][a] = r;
	}
	m-=S;
	Init();/*
	if (mat.size() != m+n)
		return 0;*/
	for (int i=0;i<n+m;i++)
	{
		findNotNull(i);
		for (int j=i+1;j<m+n;j++)
		{
			sub(mat[j],mat[i],mat[j][i]/mat[i][i],i);
		}
	}
	for (int i=n+m-1;i>=0;i--)
	{
		for (int j=i-1;j>=0;j--)
		{
			sub(mat[j],mat[i],mat[j][i]/mat[i][i],i);
		}
		mat[i][n+m]/=mat[i][i];
		mat[i][i]/=mat[i][i];
	}
	double tok = 0;
	for (int i=1;i<n;i++)
	{
		if (g[0][i] != 0)
			tok +=mat[tokID(0,i)][n+m];
	}/*
	for (int i=0;i<n;i++)
	{
		for (int j=0;j<n;j++)
		{
			if (i == j || g[i][j] == 0)
			{
				printf("%3.2lf ",0.0);
			}
			else
				printf("%3.2lf ",mat[tokID(min(i,j),max(i,j))][n+m]);
		}
		printf("\n");
	}*/
	printf("%.10lf\n",1/tok);
	double res = 1/tok;
	int toAdd = (int)(res);
	res -= toAdd;
	int p1=0,q1=1,p2=1,q2=1;
	relax(res,0,1);
	relax(res,1,1);
	for (int z=0;z<1000;z++)
	{
		int p = (p1+p2);
		int q = (q1+q2);
		if (q > 10000)
			break;
		relax(res,p,q);
		double t = (p+0.0)/q;
		if (t > res)
		{
			p2 = p;
			q2 = q;
		}
		else
		{
			p1 = p;
			q1 = q;
		}
	}
	pRes += toAdd*qRes;
	printf("%d/%d\n",pRes,qRes);
	return 0;
}
