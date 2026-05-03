<template>
  <div>
    <router-link to="/admin/groups">← Назад к группам</router-link>
    <hr>

    <div v-if="loading">Загрузка...</div>

    <div v-else-if="group">
      <h2>{{ group.name }}</h2>
      <p><strong>Предмет:</strong> {{ group.subject }}</p>
      <p><strong>Преподаватель:</strong> {{ group.teacher?.email || 'Не назначен' }}</p>
      <p><strong>Учеников:</strong> {{ group.students_count }}</p>

      <!-- Назначить преподавателя -->
      <form @submit.prevent="setTeacher" class="inline-form">
        <label>
          Назначить преподавателя (ID):
          <input v-model="teacherId" type="number" placeholder="ID преподавателя" style="width: 200px;">
        </label>
        <button type="submit">Сохранить</button>
        <button type="button" @click="removeTeacher" class="secondary">Убрать</button>
      </form>
      <div v-if="teacherError" class="error">{{ teacherError }}</div>

      <hr>

      <!-- Список учеников -->
      <h3>Ученики</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>Имя</th>
            <th>Фамилия</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in group.students" :key="student.id">
            <td>{{ student.id }}</td>
            <td>{{ student.email }}</td>
            <td>{{ student.first_name || '-' }}</td>
            <td>{{ student.last_name || '-' }}</td>
            <td>
              <button @click="removeStudent(student.id)" class="danger">Удалить</button>
            </td>
          </tr>
          <tr v-if="!group.students || group.students.length === 0">
            <td colspan="5">Нет учеников</td>
          </tr>
        </tbody>
      </table>
      
      <!-- Добавление ученика -->
      <form @submit.prevent="addStudent" class="inline-form">
        <label>
          Добавить ученика (ID):
          <input v-model.number="newStudentId" type="number" placeholder="ID ученика" style="width: 200px;">
        </label>
        <button type="submit">Добавить</button>
      </form>
      <div v-if="addError" class="error">{{ addError }}</div>
    </div>

    <div v-else class="error">Группа не найдена</div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  data() {
    return {
      group: null,
      loading: true,
      teacherId: null,
      teacherError: null,
      newStudentId: null,
      addError: null
    }
  },
  async created() {
    await this.fetchGroup()
  },

  methods: {
    async fetchGroup() {
      this.loading = true

      try {
        const groupId = this.$route.params.id
        const response = await api.get(`/admin/groups/${groupId}`)
        this.group = response.data

        if (this.group.teacher) {
          this.teacherId = this.group.teacher.id
        }
      } catch (err) {
        console.error('Ошибка загрузки группы:', err)
      } finally {
        this.loading = false
      }
    },

    async setTeacher() {
      this.teacherError = null

      try {
        const response = await api.put(`/admin/groups/${this.group.id}/teacher`, {
          teacher_id: this.teacherId || null
        })
        this.group = response.data
      } catch (err) {
        this.teacherError = err.response?.data?.error || 'Ошибка назначения преподавателя'
      }

      this.fetchGroup()
    },

    async removeTeacher() {
      this.teacherId = null
      await this.setTeacher()
    },

    async addStudent() {
      this.addError = null
      if (!this.newStudentId) {
        this.addError = 'Введите ID ученика'
        return
      }
      try {
        const response = await api.post(`/admin/groups/${this.group.id}/students`, {
          student_id: this.newStudentId
        })
        this.group = response.data
        this.newStudentId = null
      } catch (err) {
        this.addError = err.response?.data?.error || 'Ошибка добавления ученика'
      }
      this.fetchGroup()
    },

    async removeStudent(studentId) {
      try {
        const response = await api.delete(`/admin/groups/${this.group.id}/students/${studentId}`)
        this.group = response.data
      } catch (err) {
        console.error('Ошибка удаления ученика:', err)
      }
      this.fetchGroup()
    }
  },
}
</script>

<style scoped>
.inline-form {
  display: flex;
  gap: 10px;
  align-items: end;
  margin: 15px 0;
}

.error {
  color: #d32f2f;
  margin-top: 5px;
}

.danger {
  background-color: #d32f2f;
  color: white;
}
</style>