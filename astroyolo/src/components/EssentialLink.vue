<template>
  <q-item
    clickable
    tag="a"
    :to="props.to"
    :href="props.href"
    :target="props.target"
    @click="navClick"
  >
    <q-item-section
      v-if="props.icon"
      avatar
    >
      <q-icon :name="props.icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ props.title }}</q-item-label>
      <q-item-label caption>{{ props.caption }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  title: {
    type: String,
    required: true
  },

  caption: {
    type: String,
    default: ''
  },

  href: {
    type: String,
    default: undefined
  },

  to: {
    type: String,
    default: undefined
  },

  target: {
    type: String,
    default: undefined
  },

  icon: {
    type: String,
    default: ''
  }
})

// 处理导航点击事件
const navClick = (e) => {
  if (props.to) {
    e.preventDefault()
    router.push(props.to)
  } else if (props.href && props.href !== '#') {
    // For external links (with href and not just '#'),
    // we don't call e.preventDefault().
    // The browser will handle navigation, including target='_blank'.
  } else {
    // If it's neither a 'to' link nor a valid 'href' link (e.g., href='#'), prevent default.
    e.preventDefault()
  }
}
</script>
