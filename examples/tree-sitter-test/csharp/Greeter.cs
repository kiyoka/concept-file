namespace Example;

public class Greeter
{
    public string Name { get; set; }

    public Greeter(string name)
    {
        Name = name;
    }

    public string Greet()
    {
        return $"Hello, {Name}!";
    }
}
