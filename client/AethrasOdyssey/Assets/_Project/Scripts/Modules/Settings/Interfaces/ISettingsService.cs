namespace Aethras.Modules.Settings.Interfaces
{
    /// <summary>Graphics, audio, accessibility, and input settings persistence.</summary>
    public interface ISettingsService
    {
        T GetSetting<T>(string key, T defaultValue = default);
        void SetSetting<T>(string key, T value);
        void ApplyAllSettings();
        void ResetToDefaults();
    }
}
