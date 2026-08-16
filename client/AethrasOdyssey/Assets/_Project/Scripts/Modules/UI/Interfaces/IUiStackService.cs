namespace Aethras.Modules.UI.Interfaces
{
    /// <summary>UI stack manager for menus, HUD, dialogue overlays, and loading screens.</summary>
    public interface IUiStackService
    {
        void PushScreen(string screenId);
        void PopScreen();
        void ShowModal(string modalId);
        void HideModal(string modalId);
        bool IsScreenVisible(string screenId);
    }
}
