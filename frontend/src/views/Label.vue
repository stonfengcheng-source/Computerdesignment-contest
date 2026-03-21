<template>
  <div class="label">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>待标注数据池 (游戏生态语料)</span>

                <div class="crawler-controls" style="display: flex; gap: 10px; align-items: center;">
                  <el-tag type="info" size="small" effect="plain">
                    🔍 智能相似度匹配模式
                  </el-tag>
                  <el-select v-model="crawlForm.platform" size="small" style="width: 120px;" :disabled="isCrawling">
                    <el-option label="B站热搜榜" value="bilibili" />
                    <el-option label="贴吧游戏区" value="tieba" />
                    <el-option label="小红书热点" value="xhs" />
                    <el-option label="微博游戏榜" value="weibo" />
                  </el-select>
                  <el-button type="primary" size="small" :loading="isCrawling" @click="executeCrawl">
                    {{ isCrawling ? '网络探索中...' : '一键主动巡视' }}
                  </el-button>
                </div>
              </div>

              <div v-if="isCrawling || crawlProgress === 100" class="progress-container" style="margin-top: 15px;">
                <el-progress :percentage="crawlProgress" :text-inside="true" :stroke-width="18" :status="progressStatus"></el-progress>
                <div style="font-size: 12px; color: #64748b; margin-top: 5px; text-align: right;">
                  {{ crawlMessage }}
                </div>
              </div>
            </div>
          </template>

          <el-table
            :data="paginatedData"
            style="width: 100%"
            :row-class-name="tableRowClassName"
            @row-click="selectRow"
          >
            <el-table-column prop="id" label="ID" width="100" />
            <el-table-column prop="text" label="文本内容" min-width="200">
              <template #default="scope">
                <div class="text-content" :title="scope.row.text">{{ scope.row.text }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="source" label="来源" width="100">
              <template #default="scope">
                <el-tag size="small" effect="plain">{{ scope.row.source }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="时间" width="140" />
            <el-table-column label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.annotated ? 'success' : 'warning'" size="small">
                  {{ scope.row.annotated ? '已标注' : '待标注' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next"
            class="pagination"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card v-if="selectedItem" shadow="hover" class="annotation-card">
          <template #header>
            <div class="card-header">数据标注与纠偏</div>
          </template>

          <div class="selected-text">
            <h4>当前标注文本：</h4>
            <p>{{ selectedItem.text }}</p>
          </div>

          <el-form :model="annotation" label-width="120px">
            <el-divider>文本语义标注</el-divider>
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
                <el-checkbox label="小黑子">小黑子</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="是否地域黑">
              <el-switch v-model="annotation.isRegionalDiscrimination" />
            </el-form-item>

            <el-form-item label="情感极性">
              <el-select v-model="annotation.sentiment" placeholder="请判断文本情绪">
                <el-option label="正面/友善" value="positive" />
                <el-option label="负面/恶劣" value="negative" />
                <el-option label="中性/客观" value="neutral" />
              </el-select>
            </el-form-item>

            <el-divider>账号行为标注</el-divider>
            <el-form-item label="行为模式异常">
              <el-switch v-model="annotation.isAbnormal" />
            </el-form-item>

            <el-form-item v-if="annotation.isAbnormal" label="异常类型">
              <el-checkbox-group v-model="annotation.abnormalTypes">
                <el-checkbox label="水军刷屏">水军刷屏</el-checkbox>
                <el-checkbox label="人身攻击">人身攻击</el-checkbox>
                <el-checkbox label="引战钓鱼">引战钓鱼</el-checkbox>
                <el-checkbox label="违规引流">违规引流</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="submitAnnotation" class="submit-btn" size="large">
                提交并反馈给模型 (RLHF)
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card v-else shadow="hover" class="annotation-card">
          <el-empty description="请从左侧语料池中选择一条数据开始标注" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const crawlForm = ref({
  platform: 'tieba' // 默认贴吧游戏区
})

// === 进度控制状态 ===
const isCrawling = ref(false)
const crawlProgress = ref(0)
const crawlMessage = ref('')
let pollingTimer = null

const progressStatus = computed(() => {
  if (crawlProgress.value === 100) return 'success'
  if (crawlMessage.value.includes('失败') || crawlMessage.value.includes('异常')) return 'exception'
  return ''
})

const tableData = ref([])

const fetchTableData = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/v1/data/unlabeled')
    if (res.data && res.data.data) {
      tableData.value = res.data.data
    }
  } catch (error) {
    ElMessage.error('无法连接数据库获取语料')
  }
}

// === 执行爬虫逻辑 ===
const executeCrawl = async () => {
  isCrawling.value = true
  crawlProgress.value = 0
  crawlMessage.value = '系统正连接底层探针...'

  try {
    const formData = new FormData()
    formData.append('platform', crawlForm.value.platform)

    // 1. 下发任务，拿到 task_id
    const res = await axios.post('http://127.0.0.1:8000/api/v1/data/crawl', formData)
    const taskId = res.data.task_id

    // 2. 启动轮询器，每 800ms 查询一次状态
    pollingTimer = setInterval(async () => {
      try {
        const progRes = await axios.get(`http://127.0.0.1:8000/api/v1/data/crawl/progress/${taskId}`)
        const status = progRes.data.status

        crawlProgress.value = progRes.data.progress
        crawlMessage.value = progRes.data.message

        if (status === 'completed') {
          clearInterval(pollingTimer)
          isCrawling.value = false
          ElMessage.success('语料抓取完毕并已完成自动相似度打标！')
          await fetchTableData() // 自动刷新列表，显示最新入库的数据
          // 3秒后隐藏进度条
          setTimeout(() => { crawlProgress.value = 0 }, 3000)
        } else if (status === 'failed') {
          clearInterval(pollingTimer)
          isCrawling.value = false
          ElMessage.error(progRes.data.message)
        }
      } catch (err) {
        clearInterval(pollingTimer)
        isCrawling.value = false
        ElMessage.error('查询爬虫进度失败')
      }
    }, 800)

  } catch (error) {
    isCrawling.value = false
    ElMessage.error('启动网络探索任务失败')
  }
}

// === 分页及标注逻辑 ===
const currentPage = ref(1)
const pageSize = ref(10)
const total = computed(() => tableData.value.length)

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return tableData.value.slice(start, end)
})

const selectedItem = ref(null)

const annotation = ref({
  isSarcastic: '',
  hasSlang: [],
  isRegionalDiscrimination: false,
  sentiment: '',
  isAbnormal: false,
  abnormalTypes: []
})

const selectRow = (row) => {
  selectedItem.value = row
  annotation.value = {
    isSarcastic: '',
    hasSlang: [],
    isRegionalDiscrimination: false,
    sentiment: '',
    isAbnormal: false,
    abnormalTypes: []
  }
}

const tableRowClassName = ({ row }) => {
  return row.annotated ? 'annotated-row' : ''
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// === 核心修改：将标注结果提交至后端 ===
const submitAnnotation = async () => {
  if (!selectedItem.value) return ElMessage.warning('请先选择要标注的数据')

  try {
    // 调用后端新增加的 annotate 接口
    await axios.post(`http://127.0.0.1:8000/api/v1/data/annotate/${selectedItem.value.id}`, annotation.value)

    // 提交成功后，更新本地状态，表格这行会变绿
    selectedItem.value.annotated = true
    ElMessage.success('数据已成功打标！特征已持久化入库')

    // 清空右侧表单选择，提示用户继续下一条
    selectedItem.value = null
  } catch (error) {
    ElMessage.error('标注提交失败，请检查后端引擎状态')
    console.error(error)
  }
}

onMounted(() => {
  fetchTableData()
})
</script>

<style scoped>
.label {
  padding: 20px;
  background-color: #f8fafc;
  min-height: 100vh;
}
.data-card, .annotation-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  color: #334155;
  height: calc(100vh - 80px);
  overflow-y: auto;
}
.card-header {
  color: #334155;
  font-weight: 500;
}
.text-content {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.annotated-row {
  background-color: rgba(103, 194, 58, 0.08) !important;
}
.pagination {
  margin-top: 20px;
  justify-content: center;
}
.selected-text {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #e2e8f0;
  border-radius: 8px;
}
.selected-text h4 {
  color: #334155;
  margin-bottom: 10px;
}
.submit-btn {
  width: 100%;
  margin-top: 20px;
}
</style>