<template>
  <div>
    <router-link to="/admin/groups">← Назад к группам</router-link>
    <hr>

    <div v-if="loading">Загрузка...</div>

    <div v-else-if="group">
      <div class="group-details">
        <h2>{{ group.name }}</h2>
        <div class="details">
          <p><strong>Предмет: <br></strong> {{ group.subject }}</p>
          <p><strong>Преподаватель: <br></strong> {{ group.teacher?.email || 'Не назначен' }}</p>
          <p><strong>Учеников: <br></strong> {{ group.students_count }}</p>
        </div>
      </div>

      <div class="group-actions">
        <button @click="showEditForm = !showEditForm">
          {{ showEditForm ? 'Отмена' : 'Редактировать группу' }}
        </button>
        <button @click="deleteGroup" class="danger">Удалить группу</button>
      </div>

      <hr>

      <!-- Edit group form -->
      <form v-if="showEditForm" @submit.prevent="editGroup" class="edit-form">
        <h3>Редактировать группу</h3>
        
        <label>
          Название:
          <input v-model="editGroupData.name" type="text" required placeholder="Например: ПРОФМАТ-ЕГЭ-1">
        </label>

        <label>
          Предмет:
          <input v-model="editGroupData.subject" type="text" required placeholder="Например: math">
        </label>

        <label>
          Преподаватель (ID):
          <input v-model.number="editGroupData.teacher.id" type="number" placeholder="ID преподавателя (необязательно)">
        </label>

        <button type="submit">Сохранить</button>
        <div v-if="editError" class="error">{{ editError }}</div>
      </form>

      <div class="group-forms">
        <!-- Set teacher -->
        <form @submit.prevent="setTeacher" class="inline-form">
          <label>
            Назначить преподавателя (ID):
            <input v-model="teacherId" type="number" placeholder="ID преподавателя" style="width: 200px;">
          </label>
          <div class="add-actions">
            <button type="submit">Сохранить</button>
            <button type="button" @click="removeTeacher" class="secondary btn">Убрать</button>
          </div>
        </form>
        <div v-if="teacherError" class="error">{{ teacherError }}</div>
  
        <hr>
  
        <!-- Add student -->
        <form @submit.prevent="addStudent" class="inline-form">
          <label>
            Добавить ученика (ID):
            <input v-model.number="newStudentId" type="number" placeholder="ID ученика" style="width: 200px;">
          </label>
          <button type="submit">Добавить</button>
          <button type="button" @click="removeStudent(newStudentId)" class="secondary btn">Убрать</button>
        </form>
        <div v-if="addError" class="error">{{ addError }}</div>
      </div>

      <hr>

      <!-- Students list -->
      <h3>Ученики</h3>
      <div class="table-container">
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
      </div>
      
      
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
      addError: null,

      editError: null,
      showEditForm: false,
      editGroupData: null,
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

        this.editGroupData = {
          ...response.data,
          teacher: response.data.teacher ? { ...response.data.teacher } : { id: null }
        }

        if (this.group.teacher) {
          this.teacherId = this.group.teacher.id
        } else {
          this.teacherId = null
        }
      } catch (err) {
        console.error('Ошибка загрузки группы:', err)
      } finally {
        this.loading = false
      }
    },

    async editGroup() {
      this.editError = null
      this.loading = true
      try {
        const payload = { 
          name: this.editGroupData.name,
          subject: this.editGroupData.subject
        }

        if (this.editGroupData.teacher && this.editGroupData.teacher.id) {
          payload.teacher_id = this.editGroupData.teacher.id
        }

        const response = await api.put(`/admin/groups/${this.group.id}`, payload)

        this.group = response.data
        this.showEditForm = false
      } catch (err) {
        this.editError = err.response?.data?.error || 'Ошибка редактирования группы'
      } finally {
        this.loading = false
      }
    },

    async deleteGroup() {
      if (!confirm('Вы уверены, что хотите удалить группу?')) {
        return
      }

      try {
        await api.delete(`/admin/groups/${this.group.id}`)
        this.$router.push('/admin/groups')
      } catch (err) {
        alert('Ошибка удаления группы')
        console.error('Ошибка удаления группы:', err)
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
    },

    async removeStudent(studentId) {
      try {
        const response = await api.delete(`/admin/groups/${this.group.id}/students/${studentId}`)
        this.group = response.data
      } catch (err) {
        console.error('Ошибка удаления ученика:', err)
      }
    }
  },
}
</script>

<style scoped>
h2 {
  text-align: center;
  margin-bottom: 18px;
}

input {
  min-width: 100%;
  margin-bottom: 12px;
}

label {
  text-align: center;
}

button {
  border: none;
}

.group-forms {
  display: flex;
  flex-direction: row;
  gap: 24px;

  justify-content: space-evenly;
}

.inline-form {
  display: flex;
  flex-direction: column;
  width: 100%;

  background-color: rgba(0, 0, 0, 0.1);
  padding: 25px;
  border-radius: 25px;
  border: 2px solid #4a739a;
}

.group-details {
  text-align: center;

  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  align-items: center;
  gap: 32px;

  background-color: rgba(0, 0, 0, 0.1);
  padding: 25px;
  border-radius: 25px;
  border: 2px solid #4a739a;

  margin-bottom: 24px;
}

.details {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
  width: 100%;
}

.group-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.edit-form {
  margin-bottom: 20px;
  padding: 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.table-container {
  margin-bottom: 24px;

  max-height: 400px;
  overflow-x: auto;
  overflow-y: auto;
}

.btn {
  width: 100%;
}

.error {
  color: #d32f2f;
  margin-top: 5px;
}

.danger {
  background-color: #d32f2f;
  color: white;
}

@media (max-width: 756px) {
  .group-forms {
    flex-direction: column;
  }
}
</style>