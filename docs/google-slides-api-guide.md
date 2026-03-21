# Google Slides API 精美 PPT 制作指南

**调研日期**: 2026-03-18  
**作者**: Hulk 🟢  
**用途**: 使用 Google Slides API 自动化创建精美演示文稿

---

## 一、快速入门

### 1.1 环境配置

```bash
# 安装 Google API 客户端库
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# 或使用 pip3
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 1.2 API 认证设置

1. **访问 Google Cloud Console**: https://console.cloud.google.com/
2. **创建新项目** 或选择现有项目
3. **启用 Google Slides API**:
   - 导航到 "APIs & Services" > "Library"
   - 搜索 "Google Slides API"
   - 点击 "Enable"
4. **创建 OAuth 2.0 凭证**:
   - 导航到 "APIs & Services" > "Credentials"
   - 点击 "Create Credentials" > "OAuth client ID"
   - 选择 "Desktop app" 或 "Web application"
   - 下载 JSON 凭证文件，保存为 `credentials.json`

### 1.3 基础代码模板

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest
import os

# API 范围
SCOPES = ['https://www.googleapis.com/auth/presentations']

def get_slides_service():
    """获取 Google Slides API 服务"""
    creds = None
    
    # 检查是否存在已保存的凭证
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # 如果没有有效凭证，进行认证
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        # 保存凭证
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # 构建服务
    service = build('slides', 'v1', credentials=creds)
    return service
```

---

## 二、创建演示文稿

### 2.1 创建新演示文稿

```python
def create_presentation(title):
    """创建新的演示文稿"""
    service = get_slides_service()
    
    presentation = {
        'title': title,
        'locale': 'zh_CN'  # 设置语言为中文
    }
    
    presentation = service.presentations().create(body=presentation).execute()
    presentation_id = presentation['presentationId']
    print(f"创建演示文稿: {presentation_id}")
    
    return presentation_id
```

### 2.2 使用模板创建

```python
def create_from_template(template_id, title):
    """从模板创建演示文稿"""
    service = get_slides_service()
    
    # 复制模板
    drive_service = build('drive', 'v3', credentials=creds)
    new_file = {
        'name': title
    }
    
    copied_file = drive_service.files().copy(
        fileId=template_id,
        body=new_file
    ).execute()
    
    return copied_file['id']
```

---

## 三、幻灯片设计最佳实践

### 3.1 页面布局设计

```python
def create_title_slide(service, presentation_id, title, subtitle):
    """创建标题页"""
    requests = []
    
    # 获取演示文稿信息
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    slide_id = presentation['slides'][0]['objectId']
    
    # 更新标题
    requests.append({
        'insertText': {
            'objectId': slide_id,
            'text': title,
            'insertionIndex': 0
        }
    })
    
    # 批量执行
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
```

### 3.2 添加内容幻灯片

```python
def add_content_slide(service, presentation_id, title, content_points):
    """添加内容页"""
    requests = []
    
    # 创建新幻灯片
    create_slide_request = {
        'createSlide': {
            'objectId': 'content_slide_1',
            'insertionIndex': 1,
            'slideLayoutReference': {
                'predefinedLayout': 'TITLE_AND_BODY'
            }
        }
    }
    requests.append(create_slide_request)
    
    # 添加标题
    requests.append({
        'insertText': {
            'objectId': 'content_slide_1',
            'text': title,
            'insertionIndex': 0
        }
    })
    
    # 添加内容要点
    body_text = '\n'.join([f"• {point}" for point in content_points])
    requests.append({
        'insertText': {
            'objectId': 'content_slide_1',
            'text': body_text,
            'insertionIndex': len(title) + 1
        }
    })
    
    # 批量执行
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
```

### 3.3 高级格式化

```python
def format_text(service, presentation_id, object_id, start_index, end_index, 
                bold=False, italic=False, font_size=14, font_color=None):
    """格式化文本"""
    requests = []
    
    # 设置粗体
    if bold:
        requests.append({
            'updateTextStyle': {
                'objectId': object_id,
                'textRange': {
                    'type': 'FIXED_RANGE',
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'style': {
                    'bold': True
                },
                'fields': 'bold'
            }
        })
    
    # 设置斜体
    if italic:
        requests.append({
            'updateTextStyle': {
                'objectId': object_id,
                'textRange': {
                    'type': 'FIXED_RANGE',
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'style': {
                    'italic': True
                },
                'fields': 'italic'
            }
        })
    
    # 设置字体大小
    requests.append({
        'updateTextStyle': {
            'objectId': object_id,
            'textRange': {
                'type': 'FIXED_RANGE',
                'startIndex': start_index,
                'endIndex': end_index
            },
            'style': {
                'fontSize': {
                    'magnitude': font_size,
                    'unit': 'PT'
                }
            },
            'fields': 'fontSize'
        }
    })
    
    # 设置字体颜色
    if font_color:
        requests.append({
            'updateTextStyle': {
                'objectId': object_id,
                'textRange': {
                    'type': 'FIXED_RANGE',
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'style': {
                    'foregroundColor': {
                        'opaqueColor': {
                            'rgbColor': {
                                'red': font_color[0],
                                'green': font_color[1],
                                'blue': font_color[2]
                            }
                        }
                    }
                },
                'fields': 'foregroundColor'
            }
        })
    
    # 批量执行
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
```

---

## 四、主题与模板

### 4.1 推荐免费模板资源

| 网站 | URL | 特点 |
|------|-----|------|
| **Slidesgo** | https://slidesgo.com/ | 100% 免费，可商用，分类齐全 |
| **SlidesCarnival** | https://www.slidescarnival.com/ | 免费主题，设计精美 |
| **SlideTeam** | https://www.slideteam.net/ | 专业模板，部分免费 |
| **SuperSide** | https://www.superside.com/blog/google-slides-themes | 50+ 最佳主题合集 |
| **SketchBubble** | https://www.sketchbubble.com/ | 17+ 免费模板 |

### 4.2 应用主题

```python
def apply_theme(service, presentation_id, theme_id):
    """应用主题到演示文稿"""
    requests = []
    
    # 获取演示文稿信息
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    
    # 更新所有幻灯片的主题
    for slide in presentation['slides']:
        requests.append({
            'updateSlideProperties': {
                'objectId': slide['objectId'],
                'slideProperties': {
                    'notesPage': {
                        'pageElements': []
                    }
                },
                'fields': '*'
            }
        })
    
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
```

### 4.3 自定义主题颜色

```python
# 常用配色方案
COLOR_SCHEMES = {
    'professional': {
        'primary': (0.2, 0.3, 0.6),      # 深蓝
        'secondary': (0.8, 0.8, 0.8),    # 浅灰
        'accent': (0.9, 0.3, 0.2),       # 橙红
        'text': (0.1, 0.1, 0.1),         # 深灰
        'background': (1.0, 1.0, 1.0)    # 白色
    },
    'modern': {
        'primary': (0.1, 0.5, 0.7),      # 亮蓝
        'secondary': (0.95, 0.95, 0.95), # 近白
        'accent': (0.0, 0.7, 0.4),       # 绿色
        'text': (0.2, 0.2, 0.2),         # 深灰
        'background': (1.0, 1.0, 1.0)    # 白色
    },
    'minimal': {
        'primary': (0.0, 0.0, 0.0),      # 黑色
        'secondary': (0.6, 0.6, 0.6),    # 中灰
        'accent': (0.0, 0.0, 0.0),       # 黑色
        'text': (0.1, 0.1, 0.1),         # 深灰
        'background': (1.0, 1.0, 1.0)    # 白色
    },
    'warm': {
        'primary': (0.8, 0.4, 0.2),      # 橙色
        'secondary': (0.98, 0.95, 0.9),  # 米白
        'accent': (0.6, 0.2, 0.1),       # 深红
        'text': (0.2, 0.15, 0.1),        # 深棕
        'background': (1.0, 1.0, 1.0)    # 白色
    }
}
```

---

## 五、高级功能

### 5.1 添加图片

```python
from googleapiclient.http import MediaFileUpload

def add_image(service, presentation_id, slide_id, image_url, x, y, width, height):
    """添加图片到幻灯片"""
    requests = []
    
    # 创建图片
    requests.append({
        'createImage': {
            'objectId': 'image_1',
            'url': image_url,
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {
                    'height': {
                        'magnitude': height,
                        'unit': 'PT'
                    },
                    'width': {
                        'magnitude': width,
                        'unit': 'PT'
                    }
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': x,
                    'translateY': y,
                    'unit': 'PT'
                }
            }
        }
    })
    
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
```

### 5.2 添加图表

```python
def add_chart(service, presentation_id, slide_id, sheet_id, chart_id, x, y, width, height):
    """添加 Google Sheets 图表到幻灯片"""
    requests = []
    
    requests.append({
        'createSheetsChart': {
            'objectId': 'chart_1',
            'spreadsheetId': sheet_id,
            'chartId': chart_id,
            'linkingMode': 'LINKED',
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {
                    'height': {
                        'magnitude': height,
                        'unit': 'PT'
                    },
                    'width': {
                        'magnitude': width,
                        'unit': 'PT'
                    }
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': x,
                    'translateY': y,
                    'unit': 'PT'
                }
            }
        }
    })
    
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
```

### 5.3 批量操作优化

```python
def batch_update(service, presentation_id, requests):
    """批量执行多个请求"""
    MAX_BATCH_SIZE = 500  # API 限制
    
    # 分批执行
    for i in range(0, len(requests), MAX_BATCH_SIZE):
        batch = requests[i:i + MAX_BATCH_SIZE]
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': batch}
        ).execute()
        print(f"执行批次 {i // MAX_BATCH_SIZE + 1}")
```

---

## 六、设计原则与最佳实践

### 6.1 视觉设计原则

| 原则 | 说明 | 实现建议 |
|------|------|----------|
| **对比度** | 确保文字与背景对比明显 | 使用深色文字 + 浅色背景，或反之 |
| **一致性** | 保持字体、颜色、间距一致 | 定义主题样式，全局应用 |
| **留白** | 避免内容过于拥挤 | 每页内容不超过 6 行，行距 1.5 倍 |
| **层次** | 建立清晰的视觉层次 | 标题 > 副标题 > 正文，字号递减 |
| **对齐** | 保持元素对齐 | 使用网格系统，左/中/右对齐统一 |

### 6.2 字体推荐

| 用途 | 中文字体 | 英文字体 | 字号范围 |
|------|---------|---------|----------|
| **标题** | 思源黑体 Bold | Montserrat Bold | 32-48pt |
| **副标题** | 思源黑体 Medium | Montserrat Medium | 24-28pt |
| **正文** | 思源黑体 Regular | Open Sans Regular | 16-20pt |
| **备注** | 思源黑体 Light | Open Sans Light | 12-14pt |

### 6.3 配色建议

```python
# 可访问性配色（符合 WCAG 2.1 AA 标准）
ACCESSIBLE_COLORS = {
    'dark_text_light_bg': {
        'text': (0.0, 0.0, 0.0),      # 纯黑
        'background': (1.0, 1.0, 1.0)  # 纯白
    },
    'light_text_dark_bg': {
        'text': (1.0, 1.0, 1.0),      # 纯白
        'background': (0.1, 0.1, 0.1)  # 深灰
    },
    'blue_accent': {
        'primary': (0.0, 0.4, 0.8),   # 蓝色
        'complement': (1.0, 0.6, 0.0)  # 橙色
    }
}
```

### 6.4 内容组织

```python
# 标准演示结构
PRESENTATION_STRUCTURE = {
    'opening': {
        'slide_1': '标题页（标题 + 副标题 + 演讲者）',
        'slide_2': '目录/议程',
        'slide_3': '背景/问题陈述'
    },
    'body': {
        'section_1': '核心内容 1（3-5 页）',
        'section_2': '核心内容 2（3-5 页）',
        'section_3': '核心内容 3（3-5 页）'
    },
    'closing': {
        'slide_n-1': '总结/关键要点',
        'slide_n': 'Q&A / 联系方式'
    }
}

# 每页内容限制
CONTENT_LIMITS = {
    'max_lines_per_slide': 6,
    'max_words_per_line': 12,
    'max_slides_for_10min': 10,
    'max_slides_for_30min': 25,
    'max_slides_for_60min': 45
}
```

---

## 七、完整示例

### 7.1 创建完整演示文稿

```python
def create_professional_presentation(title, sections):
    """创建专业演示文稿"""
    service = get_slides_service()
    
    # 1. 创建演示文稿
    presentation = service.presentations().create(
        body={'title': title, 'locale': 'zh_CN'}
    ).execute()
    presentation_id = presentation['presentationId']
    
    # 2. 获取默认幻灯片
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    default_slide_id = presentation['slides'][0]['objectId']
    
    requests = []
    
    # 3. 更新标题页
    requests.append({
        'insertText': {
            'objectId': default_slide_id,
            'text': title,
            'insertionIndex': 0
        }
    })
    
    # 4. 添加内容页
    slide_index = 1
    for section in sections:
        requests.append({
            'createSlide': {
                'objectId': f'slide_{slide_index}',
                'insertionIndex': slide_index,
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE_AND_BODY'
                }
            }
        })
        
        # 添加标题和内容
        requests.append({
            'insertText': {
                'objectId': f'slide_{slide_index}',
                'text': section['title'],
                'insertionIndex': 0
            }
        })
        
        content = '\n'.join([f"• {point}" for point in section['points']])
        requests.append({
            'insertText': {
                'objectId': f'slide_{slide_index}',
                'text': content,
                'insertionIndex': len(section['title']) + 1
            }
        })
        
        slide_index += 1
    
    # 5. 批量执行
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    print(f"演示文稿创建完成: {presentation_id}")
    print(f"访问链接: https://docs.google.com/presentation/d/{presentation_id}/edit")
    
    return presentation_id

# 使用示例
if __name__ == '__main__':
    sections = [
        {
            'title': '项目背景',
            'points': [
                '市场现状分析',
                '用户需求洞察',
                '竞争格局概览'
            ]
        },
        {
            'title': '解决方案',
            'points': [
                '核心功能介绍',
                '技术架构说明',
                '差异化优势'
            ]
        },
        {
            'title': '实施计划',
            'points': [
                '第一阶段：MVP 开发',
                '第二阶段：用户测试',
                '第三阶段：正式发布'
            ]
        }
    ]
    
    create_professional_presentation('一念万相项目路演', sections)
```

---

## 八、常见问题与解决方案

### 8.1 认证问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `credentials.json not found` | 凭证文件缺失 | 从 Google Cloud Console 重新下载 |
| `token.json expired` | 凭证过期 | 删除 token.json，重新认证 |
| `insufficient permissions` | API 范围不足 | 检查 SCOPES 是否包含 slides 权限 |

### 8.2 API 限制

| 限制类型 | 限制值 | 应对策略 |
|----------|--------|----------|
| 每请求操作数 | 500 | 分批执行批量请求 |
| 每分钟请求数 | 300 | 添加请求延迟，使用指数退避 |
| 每日请求数 | 无硬性限制 | 监控配额使用情况 |

### 8.3 设计问题

| 问题 | 解决方案 |
|------|----------|
| 文字溢出 | 使用文本自动缩放，或减少内容 |
| 图片变形 | 保持宽高比，使用 `scaleX = scaleY` |
| 颜色不一致 | 定义全局配色方案，使用变量 |
| 字体缺失 | 使用 Google Fonts 或系统字体 |

---

## 九、资源链接

### 9.1 官方文档

- **Google Slides API 文档**: https://developers.google.com/slides
- **Python 快速入门**: https://developers.google.com/slides/api/quickstart/python
- **API 参考**: https://developers.google.com/slides/api/reference/rest
- **Google Cloud Console**: https://console.cloud.google.com/

### 9.2 模板资源

- **Slidesgo**: https://slidesgo.com/
- **SlidesCarnival**: https://www.slidescarnival.com/
- **SuperSide 主题合集**: https://www.superside.com/blog/google-slides-themes

### 9.3 工具与库

- **google-api-python-client**: `pip install google-api-python-client`
- **google-auth-oauthlib**: `pip install google-auth-oauthlib`
- **google-auth-httplib2**: `pip install google-auth-httplib2`

---

## 十、下一步行动

1. **设置 API 凭证** - 在 Google Cloud Console 创建项目并启用 Slides API
2. **安装依赖** - `pip install google-api-python-client google-auth-oauthlib`
3. **运行示例代码** - 测试基础功能
4. **选择模板** - 从 Slidesgo 或 SlidesCarnival 下载主题
5. **定制样式** - 根据品牌调整配色和字体
6. **批量生成** - 使用脚本自动化创建多份演示文稿

---

*文档版本：1.0*  
*最后更新：2026-03-18*  
*维护者：Hulk 🟢*
