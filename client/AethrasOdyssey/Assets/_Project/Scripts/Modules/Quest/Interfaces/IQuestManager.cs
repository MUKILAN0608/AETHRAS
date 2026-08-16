namespace Aethras.Modules.Quest.Interfaces
{
    /// <summary>Tracks narrative quests, objectives, and permanent world consequences.</summary>
    public interface IQuestManager
    {
        void StartQuest(string questId);
        void CompleteObjective(string questId, string objectiveId);
        bool IsQuestActive(string questId);
        bool IsQuestCompleted(string questId);
        void ApplyPermanentConsequence(string consequenceTag);
    }
}
