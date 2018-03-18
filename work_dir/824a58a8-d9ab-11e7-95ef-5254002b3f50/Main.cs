using System;
class Program {
    public static void Main() {
        byte[] buffer = new byte[0x1000000];
        for (int i = 0; i < 0x1000000; i+= 4096) {
            buffer[i] = 1;
        }
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