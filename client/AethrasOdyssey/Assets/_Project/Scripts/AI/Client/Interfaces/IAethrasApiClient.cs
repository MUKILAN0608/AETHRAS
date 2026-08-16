using System.Threading;
using System.Threading.Tasks;
using Aethras.AI.Client.DTOs;

namespace Aethras.AI.Client.Interfaces
{
    /// <summary>
    /// Low-level REST client contract for Python FastAPI backend.
    /// Only Infrastructure and AI.Client implementations should use this directly.
    /// </summary>
    public interface IAethrasApiClient
    {
        Task<ApiResponseDto<T>> GetAsync<T>(string endpoint, CancellationToken cancellationToken = default);
        Task<ApiResponseDto<T>> PostAsync<T>(string endpoint, object payload, CancellationToken cancellationToken = default);
        Task<ApiResponseDto<T>> PutAsync<T>(string endpoint, object payload, CancellationToken cancellationToken = default);
        Task<ApiResponseDto<T>> DeleteAsync<T>(string endpoint, CancellationToken cancellationToken = default);
        bool IsConnected { get; }
    }
}
