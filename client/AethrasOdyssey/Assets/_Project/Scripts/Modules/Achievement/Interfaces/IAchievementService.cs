namespace Aethras.Modules.Achievement.Interfaces
{
    /// <summary>Research-friendly achievement and milestone tracking.</summary>
    public interface IAchievementService
    {
        void UnlockAchievement(string achievementId);
        bool IsUnlocked(string achievementId);
        float GetProgress(string achievementId);
    }
}
