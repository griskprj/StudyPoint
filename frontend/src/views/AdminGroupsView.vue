<template>
  <div>
    <h2>Группы</h2>

    <div class="filters">
      <label>
        Предмет:
        <select v-model="subjectFilter" @change="fetchGroups">
          <option value="">Все</option>
          <option v-for="subj in subjects" :key="subj" :value="subj">{{ subj }}</option>
        </select>
      </label>
      <button @click="showCreateForm = !showCreateForm">
        {{ showCreateForm ? 'Отмена' : 'Создать группу' }}
      </button>
    </div>

    <!-- Create group form -->
     <form v-if="showCreateForm" @submit.prevent="createGroup" class="create-form">
      <h3>Новая группа</h3>

      <label>
        Название:
        <input v-model="newGroup.name" type="text" required placeholder="Например: ПРОФМАТ-ЕГЭ-1">
      </label>

      <label>
        Предмет:
        <input v-model="newGroup.subject" type="text" required placeholder="Например: math">
      </label>

      <label>
        Преподаватель (ID):
        <input v-model.number="newGroup.teacher_id" type="number" placeholder="ID преподавателя (необязательно)">
      </label>

      <button type="submit">Создать</button>
      <div v-if="createError" class="error">{{ createError }}</div>
     </form>

     <!-- Таблица групп -->
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Предмет</th>
            <th>Преподаватель</th>
            <th>Учеников</th>
            <th>Активна</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="group in filteredGroups" :key="group.id">
            <td>{{ group.id }}</td>
            <td>{{ group.name }}</td>
            <td>{{ group.subject }}</td>
            <td>{{ group.teacher?.email || '-' }}</td>
            <td>{{ group.students_count }}</td>
            <td>{{ group.is_active ? 'Да' : 'Нет' }}</td>
            <td>
              <router-link :to="'/admin/groups/' + group.id">Состав</router-link>
            </td>
          </tr>
          <tr v-if="filteredGroups.length === 0">
            <td colspan="7">Группы не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  data() {
    return {
      groups: [],
      subjects: [],
      subjectFilter: '',
      showCreateForm: false,
      newGroup: {
        name: '',
        subject: '',
        teacher_id: null
      },
      createError: null
    }
  },

  computed: {
    filteredGroups() {
      if (!this.subjectFilter) return this.groups
      return this.groups.filter(g => g.subject === this.subjectFilter)
    }
  },

  async created() {
    await this.fetchGroups()
  },

  methods: {
    async fetchGroups() {
      try {
        const response = await api.get('/admin/groups')
        this.groups = response.data
        this.subjects = [...new Set(this.groups.map(g => g.subject))]
      } catch (err) {
        console.error('Ошибка загрузки групп:', err)
      }
    },
    async createGroup() {
      this.createError = null
      try {
        const payload = { ...this.newGroup }
        if (!payload.teacher_id) delete payload.teacher_id

        const response = await api.post('/admin/groups', payload)
        this.groups.push(response.data)
        this.subjects = [...new Set(this.groups.map(g => g.subject))]

        this.newGroup = { name: '', subject: '', teacher_id: null }
        this.showCreateForm = false
      } catch (err) {
        this.createError = err.response?.data?.error || 'Ошибка создания группы'
      }
    }
  }
}
</script>

<style scoped>
.filters {
  display: flex;
  flex-direction: column;
  margin-bottom: 24px;
}

.table-container {
  overflow-y: auto;
  overflow-x: auto;
}

.create-form {
  margin-bottom: 20px;
  padding: 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.error {
  color: #d32f2f;
  margin-top: 10px;
}
</style>