<template>
  <div class="container">
    <h1>Панель администратора</h1>

    <nav>
      <ul>
        <li><router-link to="/admin/users">Пользователи</router-link></li>
        <li><router-link to="/admin/groups">Группы</router-link></li>
      </ul>
    </nav>

    <hr>

    <router-view />
  </div>
</template>