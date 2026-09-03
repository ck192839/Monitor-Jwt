<template>
  <div class="auth-view reset-view">
    <el-button class="back-button" link :icon="ArrowLeft" @click="router.push('/')">返回登录</el-button>
    <el-steps class="reset-steps" :active="active" finish-status="success" simple>
      <el-step title="验证邮箱"/>
      <el-step title="设置密码"/>
    </el-steps>
    <transition name="el-fade-in-linear" mode="out-in">
      <div v-if="active === 0" key="verify">
        <div class="auth-heading">
          <h2>找回账户密码</h2>
          <p>验证账户绑定的电子邮件地址</p>
        </div>
        <el-form class="auth-form" :model="form" :rules="rules"
                 @validate="onValidate" ref="formRef">
          <el-form-item prop="email">
            <el-input v-model="form.email" type="email" autocomplete="email" placeholder="电子邮件地址">
              <template #prefix>
                <el-icon><Message/></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="code">
            <div class="code-row">
              <el-input v-model="form.code" :maxlength="6" type="text" placeholder="验证码">
                <template #prefix>
                  <el-icon><EditPen/></el-icon>
                </template>
              </el-input>
              <el-button class="code-button" type="primary" plain @click="validateEmail"
                         :disabled="!isEmailValid || coldTime > 0">
                {{coldTime > 0 ? coldTime + ' 秒后重试' : '获取验证码'}}
              </el-button>
            </div>
          </el-form-item>
          <el-button class="auth-submit" @click="confirmReset()" type="primary">验证并继续</el-button>
        </el-form>
      </div>
      <div v-else key="reset">
        <div class="auth-heading">
          <h2>设置新密码</h2>
          <p>密码长度为 6 至 16 个字符</p>
        </div>
        <el-form class="auth-form" :model="form" :rules="rules"
                 @validate="onValidate" ref="formRef">
          <el-form-item prop="password">
            <el-input v-model="form.password" :maxlength="16" type="password"
                      autocomplete="new-password" placeholder="新密码" show-password>
              <template #prefix>
                <el-icon><Lock/></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="password_repeat">
            <el-input v-model="form.password_repeat" :maxlength="16" type="password"
                      autocomplete="new-password" placeholder="再次输入新密码" show-password
                      @keyup.enter="doReset">
              <template #prefix>
                <el-icon><Lock/></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-button class="auth-submit" @click="doReset()" type="primary">确认重置密码</el-button>
        </el-form>
      </div>
    </transition>
  </div>
</template>

<script setup>
import {reactive, ref} from "vue";
import {ArrowLeft, EditPen, Lock, Message} from "@element-plus/icons-vue";
import {get, post} from "@/net";
import {ElMessage} from "element-plus";
import router from "@/router";

const active = ref(0)

const form = reactive({
  email: '',
  code: '',
  password: '',
  password_repeat: '',
})

const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error("两次输入的密码不一致"))
  } else {
    callback()
  }
}

const rules = {
  email: [
    { required: true, message: '请输入邮件地址', trigger: 'blur' },
    {type: 'email', message: '请输入合法的电子邮件地址', trigger: ['blur', 'change']}
  ],
  code: [
    { required: true, message: '请输入获取的验证码', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 16, message: '密码的长度必须在6-16个字符之间', trigger: ['blur'] }
  ],
  password_repeat: [
    { validator: validatePassword, trigger: ['blur', 'change'] },
  ],
}

const formRef = ref()
const isEmailValid = ref(false)
const coldTime = ref(0)

const onValidate = (prop, isValid) => {
  if(prop === 'email')
    isEmailValid.value = isValid
}

const validateEmail = () => {
  coldTime.value = 60
  get(`/api/auth/ask-code?email=${form.email}&type=reset`, () => {
    ElMessage.success(`验证码已发送到邮箱: ${form.email}，请注意查收`)
    const handle = setInterval(() => {
      coldTime.value--
      if(coldTime.value === 0) {
        clearInterval(handle)
      }
    }, 1000)
  }, (message) => {
    ElMessage.warning(message)
    coldTime.value = 0
  })
}

const confirmReset = () => {
  formRef.value.validate((isValid) => {
    if(isValid) {
      post('/api/auth/reset-confirm', {
        email: form.email,
        code: form.code
      }, () => active.value++)
    }
  })
}

const doReset = () => {
  formRef.value.validate((isValid) => {
    if(isValid) {
      post('/api/auth/reset-password', {
        email: form.email,
        code: form.code,
        password: form.password
      }, () => {
        ElMessage.success('密码重置成功，请重新登录')
        router.push('/')
      })
    }
  })
}
</script>

<style scoped>
.back-button {
  margin: 0 0 20px -8px;
  color: var(--el-text-color-secondary);
  transition: transform .2s ease, color .2s ease;
}

.back-button:hover {
  transform: translateX(-3px);
  color: var(--el-color-primary);
}

.reset-steps {
  margin-bottom: 34px;
  padding: 12px 16px;
  border-radius: 5px;
}

.reset-view .auth-heading {
  margin-bottom: 26px;
}

.code-row {
  width: 100%;
  display: flex;
  gap: 10px;
}

.code-row .el-input {
  min-width: 0;
  flex: 1;
}

.code-button {
  width: 116px;
  min-width: 116px;
  height: 42px;
  padding: 0 10px;
  font-size: 12px;
  border-radius: 5px;
}

@media (max-width: 380px) {
  .reset-steps {
    padding: 10px 12px;
  }

  .code-button {
    width: 104px;
    min-width: 104px;
    padding: 0 6px;
  }
}
</style>
