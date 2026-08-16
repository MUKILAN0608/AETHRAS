using System.Threading;
using System.Threading.Tasks;

namespace Aethras.Modules.Dialogue.Interfaces
{
    /// <summary>Manages dialogue flow, branching, and AI-adaptive responses.</summary>
    public interface IDialogueManager
    {
        bool IsDialogueActive { get; }
        Task StartDialogueAsync(string npcId, CancellationToken cancellationToken = default);
        Task AdvanceDialogueAsync(string playerChoiceId, CancellationToken cancellationToken = default);
        void EndDialogue();
    }
}
