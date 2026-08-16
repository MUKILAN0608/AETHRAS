using System.Threading;
using System.Threading.Tasks;

namespace Aethras.Application.Interfaces
{
    /// <summary>
    /// Cross-cutting save/load orchestration contract.
    /// </summary>
    public interface ISaveLoadService
    {
        Task<bool> SaveAsync(string slotId, CancellationToken cancellationToken = default);
        Task<bool> LoadAsync(string slotId, CancellationToken cancellationToken = default);
        Task<bool> DeleteSaveAsync(string slotId, CancellationToken cancellationToken = default);
        bool HasSave(string slotId);
    }
}
