namespace Aethras.Modules.Inventory.Interfaces
{
    /// <summary>Manages lore items, keys, and narrative inventory (no combat items).</summary>
    public interface IInventoryService
    {
        bool AddItem(string itemId);
        bool RemoveItem(string itemId);
        bool HasItem(string itemId);
        int GetItemCount(string itemId);
    }
}
