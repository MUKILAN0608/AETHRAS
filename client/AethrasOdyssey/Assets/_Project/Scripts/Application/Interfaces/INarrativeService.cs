using System.Threading;
using System.Threading.Tasks;
using Aethras.Application.DTOs;

namespace Aethras.Application.Interfaces
{
    /// <summary>
    /// Application facade for AI narrative requests.
    /// Modules call this; Infrastructure + AI.Client handle REST transport.
    /// </summary>
    public interface INarrativeService
    {
        Task<NarrativeResponseDto> RequestDialogueAsync(NarrativeRequestDto request, CancellationToken cancellationToken = default);
        Task<NarrativeResponseDto> RequestEnvironmentalEventAsync(NarrativeRequestDto request, CancellationToken cancellationToken = default);
        Task<bool> SubmitChoiceAsync(ChoiceSubmissionDto choice, CancellationToken cancellationToken = default);
        Task<MemorySyncResultDto> SyncMemoryAsync(MemorySyncRequestDto request, CancellationToken cancellationToken = default);
    }
}
