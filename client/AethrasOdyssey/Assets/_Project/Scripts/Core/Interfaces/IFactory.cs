namespace Aethras.Core.Factories
{
    /// <summary>
    /// Factory contract for creating runtime instances from ScriptableObject definitions.
    /// </summary>
    public interface IFactory<out TProduct, in TDefinition>
    {
        TProduct Create(TDefinition definition);
    }
}
