using System;
class Program {
    public static void Main() {
        string line;
        string []p;
        int a,b;
        while((line=Console.ReadLine())!=null&&line!="")

        {
            p=line.Split(' ');
            a=int.Parse(p[0]);b=int.Parse(p[1]);
            Console.WriteLine(a+b);
        }
    }
}