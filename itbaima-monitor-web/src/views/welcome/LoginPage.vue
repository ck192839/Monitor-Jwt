<template>
  <div class="auth-view">
    <div class="auth-heading">
      <h2>登录控制台</h2>
      <p>使用管理员或子账户凭据继续</p>
    </div>
    <el-form class="auth-form" :model="form" :rules="rules" ref="formRef">
      <el-form-item prop="username">
        <el-input v-model="form.username" maxlength="10" type="text"
                  autocomplete="username" placeholder="用户名或邮箱">
          <template #prefix>
            <el-icon><User/></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" maxlength="20"
                  autocomplete="current-password" placeholder="密码" show-password
                  @keyup.enter="userLogin">
          <template #prefix>
            <el-icon><Lock/></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <div class="login-options">
        <el-form-item prop="remember">
          <el-checkbox v-model="form.remember" label="记住我"/>
        </el-form-item>
        <el-link type="primary" :underline="false" @click="router.push('/forget')">忘记密码？</el-link>
      </div>
      <el-button class="auth-submit" @click="userLogin()" type="primary">立即登录</el-button>
    </el-form>
  </div>
</template>

<script setup>
import {User, Lock} from '@element-plus/icons-vue'
import router from "@/router";
import {reactive, ref} from "vue";
import {login} from '@/net'

const formRef = ref()
const form = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名' }
  ],
  password: [
    { required: true, message: '请输入密码'}
  ]
}

function userLogin() {
  formRef.value.validate((isValid) => {
    if(isValid) {
      login(form.username, form.password, form.remember, () => router.push("/index"))
    }
  });
}
</script>

<style scoped>
.login-options {
  min-height: 32px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.login-options :deep(.el-form-item) {
  margin-bottom: 0;
}

.login-options .el-link {
  margin-top: 5px;
  font-size: 13px;
}
</style>
