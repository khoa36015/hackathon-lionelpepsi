<script>
  export let tourItems = [];
  export let tourName = "";
  
  // Group items by location
  function groupByLocation(items) {
    const groups = {};
    items.forEach((item, index) => {
      // Try different possible location field names
      const location = item.dia_diem || item.location || item.location_hint || "Không xác định";
      if (!groups[location]) {
        groups[location] = [];
      }
      groups[location].push({ ...item, originalIndex: index });
    });
    return groups;
  }
  
  // Get item name (handle both 'name' and 'ten' fields)
  function getItemName(item) {
    return item.name || item.ten || 'Không tên';
  }
  
  // Get item description
  function getItemDescription(item) {
    return item.description || item.mo_ta || item.period || '';
  }
  
  $: locationGroups = groupByLocation(tourItems);
  $: locations = Object.keys(locationGroups);
</script>

<div class="tour-diagram">
  {#if tourItems.length === 0}
    <div class="empty-state">
      <p class="text-gray-400">Chưa có điểm tham quan trong lịch trình</p>
    </div>
  {:else}
    <div class="diagram-container">
      <!-- Timeline/Flow Diagram -->
      <div class="flow-diagram">
        {#each locations as location, locIndex}
          <div class="location-group" style="animation-delay: {locIndex * 0.1}s">
            <!-- Location Header -->
            <div class="location-header">
              <div class="location-icon">📍</div>
              <div class="location-info">
                <h3 class="location-name">{location}</h3>
                <p class="location-count">{locationGroups[location].length} điểm tham quan</p>
              </div>
            </div>
            
            <!-- Items in this location -->
            <div class="items-grid">
              {#each locationGroups[location] as item, itemIndex}
                <div class="item-card" style="animation-delay: {(locIndex * 0.1) + (itemIndex * 0.05)}s">
                  <div class="item-number">{item.order || item.originalIndex + 1}</div>
                  <div class="item-content">
                    <div class="item-icon">
                      {#if item.type === 'photo'}
                        📷
                      {:else}
                        🏺
                      {/if}
                    </div>
                    <h4 class="item-name">{getItemName(item)}</h4>
                    {#if getItemDescription(item)}
                      <p class="item-meta">
                        {getItemDescription(item).substring(0, 50)}
                        {#if getItemDescription(item).length > 50}...{/if}
                      </p>
                    {/if}
                  </div>
                  
                  <!-- Arrow to next item -->
                  {#if itemIndex < locationGroups[location].length - 1 || locIndex < locations.length - 1}
                    <div class="arrow-down">
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M10 15L5 10L10 5M15 10L10 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
            
            <!-- Arrow to next location -->
            {#if locIndex < locations.length - 1}
              <div class="location-arrow">
                <div class="arrow-line"></div>
                <div class="arrow-head">→</div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
      
      <!-- Summary Stats -->
      <div class="summary-stats">
        <div class="stat-card">
          <div class="stat-value">{tourItems.length}</div>
          <div class="stat-label">Tổng điểm tham quan</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{locations.length}</div>
          <div class="stat-label">Số địa điểm</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{tourItems.filter(i => i.type === 'photo').length}</div>
          <div class="stat-label">Ảnh lịch sử</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{tourItems.filter(i => i.type === 'artifact').length}</div>
          <div class="stat-label">Di vật</div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .tour-diagram {
    width: 100%;
    padding: 2rem;
  }
  
  .empty-state {
    text-align: center;
    padding: 3rem;
  }
  
  .diagram-container {
    width: 100%;
  }
  
  .flow-diagram {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    margin-bottom: 2rem;
  }
  
  .location-group {
    background: linear-gradient(135deg, rgba(196, 165, 116, 0.1) 0%, rgba(42, 42, 42, 0.5) 100%);
    border: 2px solid rgba(196, 165, 116, 0.3);
    border-radius: 1rem;
    padding: 1.5rem;
    animation: slideInUp 0.6s ease-out forwards;
    opacity: 0;
  }
  
  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .location-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid rgba(196, 165, 116, 0.2);
  }
  
  .location-icon {
    font-size: 2rem;
  }
  
  .location-info {
    flex: 1;
  }
  
  .location-name {
    font-size: 1.25rem;
    font-weight: bold;
    color: #c4a574;
    margin: 0 0 0.25rem 0;
  }
  
  .location-count {
    font-size: 0.875rem;
    color: #9ca3af;
    margin: 0;
  }
  
  .items-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .item-card {
    background: rgba(26, 26, 26, 0.8);
    border: 1px solid rgba(196, 165, 116, 0.2);
    border-radius: 0.75rem;
    padding: 1rem;
    position: relative;
    transition: all 0.3s ease;
    animation: fadeIn 0.5s ease-out forwards;
    opacity: 0;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
  
  .item-card:hover {
    border-color: #c4a574;
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(196, 165, 116, 0.2);
  }
  
  .item-number {
    position: absolute;
    top: -10px;
    right: -10px;
    background: #c4a574;
    color: #1a1a1a;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 0.875rem;
  }
  
  .item-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .item-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }
  
  .item-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .item-meta {
    font-size: 0.75rem;
    color: #9ca3af;
    margin: 0;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .arrow-down {
    position: absolute;
    bottom: -15px;
    left: 50%;
    transform: translateX(-50%);
    color: #c4a574;
    opacity: 0.5;
  }
  
  .location-arrow {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 1rem 0;
    color: #c4a574;
  }
  
  .arrow-line {
    width: 2px;
    height: 40px;
    background: linear-gradient(to bottom, #c4a574, transparent);
    margin-bottom: 0.5rem;
  }
  
  .arrow-head {
    font-size: 1.5rem;
    animation: bounce 2s infinite;
  }
  
  @keyframes bounce {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(5px);
    }
  }
  
  .summary-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 2rem;
  }
  
  .stat-card {
    background: rgba(196, 165, 116, 0.1);
    border: 1px solid rgba(196, 165, 116, 0.2);
    border-radius: 0.75rem;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
  }
  
  .stat-card:hover {
    background: rgba(196, 165, 116, 0.15);
    transform: translateY(-4px);
  }
  
  .stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: #c4a574;
    margin-bottom: 0.5rem;
  }
  
  .stat-label {
    font-size: 0.875rem;
    color: #9ca3af;
  }
  
  @media (max-width: 768px) {
    .tour-diagram {
      padding: 1rem;
    }
    
    .items-grid {
      grid-template-columns: 1fr;
    }
    
    .summary-stats {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>

