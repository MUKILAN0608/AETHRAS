namespace Aethras.Modules.Analytics.Interfaces
{
    /// <summary>Research telemetry: choice patterns, exploration heatmaps, session metrics.</summary>
    public interface IAnalyticsService
    {
        void TrackEvent(string eventName, System.Collections.Generic.Dictionary<string, object> properties = null);
        void StartSession(string sessionId);
        void EndSession();
        void Flush();
    }
}
