namespace Aethras.Modules.Audio.Interfaces
{
    /// <summary>Layered audio: music, ambience, SFX, adaptive horror mixing.</summary>
    public interface IAudioDirector
    {
        void PlayMusic(string trackId, float fadeDuration = 1f);
        void PlayAmbience(string ambienceId);
        void PlaySfx(string sfxId);
        void SetMasterVolume(float volume);
        void SetAdaptiveIntensity(float intensity);
    }
}
