namespace Aethras.Modules.Choice.Interfaces
{
    /// <summary>Records permanent player choices and publishes consequence events.</summary>
    public interface IChoiceEngine
    {
        void RecordChoice(string choiceId, string worldId, string consequenceTag);
        bool HasMadeChoice(string choiceId);
        bool HasConsequence(string consequenceTag);
    }
}
