#include<iostream>
using namespace std;
int main()
{
  int no;
  cin>>no;
  string p="Possible";
  string np="Not possible";
  int value = no%2;
  string yes = value==0 ? p : np;
  cout<<yes;
}