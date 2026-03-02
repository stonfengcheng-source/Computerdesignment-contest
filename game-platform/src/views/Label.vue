<template>
  <div class="label">
    <el-row :gutter="20">
      <!-- 左侧数据列表 -->
      <el-col :span="12">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">待标注数据</div>
          </template>

          <el-table
            :data="paginatedData"
            style="width: 100%"
            :row-class-name="tableRowClassName"
            @row-click="selectRow"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="text" label="文本内容" min-width="200">
              <template #default="scope">
                <div class="text-content">{{ scope.row.text }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="source" label="来源" width="100" />
            <el-table-column prop="time" label="时间" width="150" />
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.annotated ? 'success' : 'warning'">
                  {{ scope.row.annotated ? '已标注' : '待标注' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20, 50]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            class="pagination"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </el-card>
      </el-col>

      <!-- 右侧标注面板 -->
      <el-col :span="12">
        <el-card v-if="selectedItem" shadow="hover" class="annotation-card">
          <template #header>
            <div class="card-header">数据标注</div>
          </template>

          <div class="selected-text">
            <h4>当前标注文本：</h4>
            <p>{{ selectedItem.text }}</p>
          </div>

          <el-form :model="annotation" label-width="120px">
            <!-- 文本标注 -->
            <el-divider>文本标注</el-divider>

            <el-form-item label="是否阴阳怪气">
              <el-radio-group v-model="annotation.isSarcastic">
                <el-radio label="是">是</el-radio>
                <el-radio label="否">否</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="是否包含黑话">
              <el-checkbox-group v-model="annotation.hasSlang">
                <el-checkbox label="下饭">下饭</el-checkbox>
                <el-checkbox label="演员">演员</el-checkbox>
                <el-checkbox label="摆烂">摆烂</el-checkbox>
                <el-checkbox label="内卷">内卷</el-checkbox>
                <el-checkbox label="emo">emo</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="情感极性">
              <el-select v-model="annotation.sentiment" placeholder="请选择">
                <el-option label="正面" value="positive" />
                <el-option label="负面" value="negative" />
                <el-option label="中性" value="neutral" />
              </el-select>
            </el-form-item>

            <!-- 行为标注 -->
            <el-divider>行为标注</el-divider>

            <el-form-item label="是否异常">
              <el-switch v-model="annotation.isAbnormal" />
            </el-form-item>

            <el-form-item v-if="annotation.isAbnormal" label="异常类型">
              <el-checkbox-group v-model="annotation.abnormalTypes">
                <el-checkbox label="刷屏">刷屏</el-checkbox>
                <el-checkbox label="辱骂">辱骂</el-checkbox>
                <el-checkbox label="广告">广告</el-checkbox>
                <el-checkbox label="违规链接">违规链接</el-checkbox>
                <el-checkbox label="其他">其他</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="submitAnnotation" class="submit-btn">
                提交标注
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card v-else shadow="hover" class="annotation-card">
          <el-empty description="请先选择左侧的数据进行标注" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Mock 数据
const mockData = ref([
  {
    id: 1,
    text: '这游戏真下饭，玩得我都想摆烂了',
    source: '论坛',
    time: '2024-02-23 10:00',
    annotated: false
  },
  {
    id: 2,
    text: '今天心情不错，emo 了一整天',
    source: '微博',
    time: '2024-02-23 11:30',
    annotated: false
  },
  {
    id: 3,
    text: '这个活动太卷了，完全不想参加',
    source: '贴吧',
    time: '2024-02-23 14:20',
    annotated: false
  },
  {
    id: 4,
    text: '终于通关了，感觉自己像个演员',
    source: '论坛',
    time: '2024-02-23 16:45',
    annotated: false
  },
  {
    id: 5,
    text: '天气真好，心情愉悦',
    source: '微信',
    time: '2024-02-23 18:00',
    annotated: true
  },
  {
    id: 6,
    text: '这个功能怎么这么难用，简直是灾难',
    source: '论坛',
    time: '2024-02-24 09:15',
    annotated: false
  },
  {
    id: 7,
    text: '大家一起刷屏庆祝吧！',
    source: '群聊',
    time: '2024-02-24 12:30',
    annotated: false
  },
  {
    id: 8,
    text: '推荐一个好用的工具给大家',
    source: '论坛',
    time: '2024-02-24 15:45',
    annotated: false
  }
])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = computed(() => mockData.value.length)

// 当前页数据
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return mockData.value.slice(start, end)
})

// 选中的数据项
const selectedItem = ref(null)

// 标注数据
const annotation = ref({
  isSarcastic: '',
  hasSlang: [],
  sentiment: '',
  isAbnormal: false,
  abnormalTypes: []
})

// 选择行
const selectRow = (row) => {
  selectedItem.value = row
  // 重置标注数据
  annotation.value = {
    isSarcastic: '',
    hasSlang: [],
    sentiment: '',
    isAbnormal: false,
    abnormalTypes: []
  }
}

// 表格行类名
const tableRowClassName = ({ row }) => {
  return row.annotated ? 'annotated-row' : ''
}

// 分页大小改变
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

// 当前页改变
const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 提交标注
const submitAnnotation = () => {
  if (!selectedItem.value) {
    ElMessage.warning('请先选择要标注的数据')
    return
  }

  // 这里可以发送数据到后端
  console.log('标注数据:', {
    itemId: selectedItem.value.id,
    annotation: annotation.value
  })

  // 更新状态
  selectedItem.value.annotated = true

  ElMessage.success('标注成功！')

  // 清空选择
  selectedItem.value = null
}
</script>

<style scoped>
.label {
  padding: 20px;
  background-color: #0A0F1F;
  min-height: 100vh;
}

.data-card,
.annotation-card {
  background-color: #1A1D2A;
  border: 1px solid #2A2F3A;
  color: #B0B3C1;
  height: calc(100vh - 120px);
  overflow: hidden;
}

.card-header {
  color: #B0B3C1;
  font-weight: 500;
}

.text-content {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.annotated-row {
  background-color: rgba(103, 194, 58, 0.1);
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.selected-text {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #2A2F3A;
  border-radius: 8px;
}

.selected-text h4 {
  color: #B0B3C1;
  margin-bottom: 10px;
}

.selected-text p {
  color: #B0B3C1;
  line-height: 1.6;
  margin: 0;
}

:deep(.el-divider__text) {
  color: #B0B3C1;
  background-color: #1A1D2A;
}

:deep(.el-form-item__label) {
  color: #B0B3C1;
}

:deep(.el-radio__label),
:deep(.el-checkbox__label),
:deep(.el-select-dropdown__item) {
  color: #B0B3C1;
}

:deep(.el-radio),
:deep(.el-checkbox) {
  color: #B0B3C1;
}

.submit-btn {
  width: 100%;
}

:deep(.el-empty__description p) {
  color: #7A7F8A;
}
</style>