<template>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <router-view />
</template>

<style>
@media (max-width: 768px) {
  .table-responsive {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  /* Карточный вид для таблиц на мобильных */
  .mobile-card-table {
    border: none;
  }

  .mobile-card-table thead {
    display: none;
  }

  .mobile-card-table tbody tr {
    display: block;
    margin-bottom: 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1rem;
    transition: all 0.2s;
  }

  .mobile-card-table tbody tr:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }

  .mobile-card-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border: none;
    border-bottom: 1px solid var(--border-color);
  }

  .mobile-card-table td:last-child {
    border-bottom: none;
  }

  .mobile-card-table td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-secondary);
    font-size: 0.875rem;
    margin-right: 1rem;
  }

  /* Для ячеек с действиями */
  .mobile-card-table td.col-actions {
    justify-content: flex-end;
    gap: 0.5rem;
  }

  .mobile-card-table td.col-actions::before {
    content: 'Действия';
  }

  .mobile-card-table .action-buttons {
    flex-direction: row !important;
    gap: 0.5rem;
  }
}

/* Для планшетов */
@media (min-width: 769px) and (max-width: 1024px) {
  .groups-table th,
  .groups-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.875rem;
  }

  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }

  .action-btn {
    width: 28px;
    height: 28px;
  }
}
</style>