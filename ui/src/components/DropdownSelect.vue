<template>
    <div class="dropdown-select">
        <select :value="modelValue ?? ''" @change="onChange">
            <option
                v-for="option in options"
                :key="String(option[valueKey])"
                :value="String(option[valueKey])"
            >
                {{ String(option[labelKey]) }}
            </option>
        </select>
    </div>
</template>

<script setup lang="ts">
type OptionValue = string | number | boolean

type OptionItem = {
  [key: string]: OptionValue
}

const props = withDefaults(
  defineProps<{
    modelValue: OptionValue | null
    options: OptionItem[]
    labelKey?: string
    valueKey?: string
  }>(),
  {
    modelValue: null,
    labelKey: "label",
    valueKey: "value"
  }
)

const emit = defineEmits<{
  (e: "update:modelValue", value: number): void
}>()

function onChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit("update:modelValue", Number(target.value))
}
</script>

<style scoped>
.dropdown-select {
  display: inline-block;
  position: relative;
}

.dropdown-select select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;

  padding: 8px 36px 8px 14px;
  border-radius: 999px;

  border: none;
  background: #ededed;

  font-size: 0.9rem;
  font-weight: 500;
  color: #333;

  cursor: pointer;
}

/* custom arrow */
.dropdown-select::after {
  content: "▾";
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  font-size: 0.8rem;
  color: #666;
}

.dropdown-select select:hover {
  border-color: #bbb;
}

.dropdown-select select:focus {
  outline: none;
  border-color: #111;
}
</style>