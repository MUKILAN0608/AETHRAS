namespace Aethras.Application.DTOs
{
    /// <summary>Transport DTO for narrative API requests.</summary>
    public sealed class NarrativeRequestDto
    {
        public string SessionId { get; set; }
        public string WorldId { get; set; }
        public string NpcId { get; set; }
        public string ContextTag { get; set; }
        public string PlayerInput { get; set; }
    }

    /// <summary>Transport DTO for narrative API responses.</summary>
    public sealed class NarrativeResponseDto
    {
        public string ResponseId { get; set; }
        public string Text { get; set; }
        public string[] SuggestedChoices { get; set; }
        public bool IsValidated { get; set; }
    }

    /// <summary>Player choice submission to backend memory graph.</summary>
    public sealed class ChoiceSubmissionDto
    {
        public string SessionId { get; set; }
        public string ChoiceId { get; set; }
        public string WorldId { get; set; }
        public string ConsequenceTag { get; set; }
    }

    /// <summary>Memory sync request for cross-world persistence.</summary>
    public sealed class MemorySyncRequestDto
    {
        public string SessionId { get; set; }
        public string[] ActiveMemoryTags { get; set; }
    }

    /// <summary>Result of memory graph synchronization.</summary>
    public sealed class MemorySyncResultDto
    {
        public bool Success { get; set; }
        public string[] UpdatedMemoryTags { get; set; }
    }
}
