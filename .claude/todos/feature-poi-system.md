# Feature: POI (Point of Interest) 시스템 개발 전략 📍

> **목표**: 360° 공간에 이미지/설명/링크를 자유롭게 추가할 수 있는 시스템 구축
> **기간**: 6-8일
> **영향도**: High (핵심 신규 기능)

---

## 🎯 기능 요구사항

### 1. 정보 POI (Info Point)
- 사용자가 원하는 위치에 이미지 + 설명 추가
- 클릭 시 상세 정보 표시
- 반응형 UI (거리에 따라 크기 조정)

### 2. 링크 POI (Link Point)
- 기존: 동서남북 4방향 고정 링크
- 개선: 사용자가 자유롭게 위치 지정
- 다른 Space로 이동하는 포털

### 3. 편집 모드
- Visual Inspector 기능
- 현재 보고 있는 방향에 POI 추가
- 드래그로 위치 조정
- 실시간 프리뷰

---

## 📊 데이터베이스 스키마

### Before (현재)
```python
# scenes collection
{
  "_id": ObjectId,
  "name": "주방",
  "image_id": ObjectId,
  "links": [ObjectId, ObjectId]  # links collection 참조
}

# links collection
{
  "_id": ObjectId,
  "target_id": ObjectId,  # 대상 씬
  "x": 0, "y": 0, "z": -6,
  "yaw": 0, "pitch": 0, "roll": 0
}
```

### After (개선)
```python
# scenes collection
{
  "_id": ObjectId,
  "name": "주방",
  "image_id": ObjectId,
  "links": [ObjectId],  # 기존 호환성 유지
  "pois": [  # 신규 추가
    {
      "poi_id": ObjectId,
      "type": "info",  # "info" | "link" | "media"
      "title": "역사적 의미",
      "description": "이 공간은 1900년에 건축되었습니다...",
      "position": {"x": 2, "y": 1.5, "z": -3},
      "rotation": {"x": 0, "y": 45, "z": 0},
      "scale": {"x": 1, "y": 1, "z": 1},
      "image_id": ObjectId,  # GridFS (선택)
      "target_scene_id": ObjectId,  # type=link인 경우
      "visible": True,
      "created_at": ISODate,
      "updated_at": ISODate
    }
  ]
}

# pois collection (신규, 선택적 정규화)
{
  "_id": ObjectId,
  "scene_id": ObjectId,
  "type": "info",
  "title": "제목",
  "description": "설명",
  "position": {"x": 0, "y": 0, "z": 0},
  "rotation": {"x": 0, "y": 0, "z": 0},
  "scale": {"x": 1, "y": 1, "z": 1},
  "image_id": ObjectId,
  "target_scene_id": ObjectId,
  "style": {
    "panel_color": "#ffffff",
    "text_color": "#000000",
    "width": 1.2,
    "height": 0.8
  },
  "visible": True,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**선택 기준**:
- **Embedded (pois 배열)**: POI 개수 < 20개, 간단한 구조
- **Referenced (별도 collection)**: POI 개수 > 20개, 복잡한 쿼리 필요

**권장**: Embedded 방식 (대부분의 씬에 10개 미만 POI 예상)

---

## 🎨 A-Frame 컴포넌트 아키텍처

### 1. poi-marker.js (POI 렌더링)
```javascript
AFRAME.registerComponent('poi-marker', {
  schema: {
    poiId: {type: 'string'},
    type: {type: 'string', default: 'info'},  // info | link
    title: {type: 'string'},
    description: {type: 'string'},
    imageUrl: {type: 'string'},
    targetSceneId: {type: 'string'}
  },

  init: function() {
    this.createMarker();
    this.setupInteractions();
  },

  createMarker: function() {
    if (this.data.type === 'info') {
      this.createInfoMarker();
    } else if (this.data.type === 'link') {
      this.createLinkMarker();
    }
  },

  createInfoMarker: function() {
    // 아이콘 (클릭 가능한 구체)
    var icon = document.createElement('a-sphere');
    icon.setAttribute('radius', 0.2);
    icon.setAttribute('color', '#4CAF50');
    icon.setAttribute('class', 'clickable poi-icon');
    icon.setAttribute('animation__hover',
      'property: scale; to: 1.2 1.2 1.2; dur: 200; startEvents: mouseenter');
    icon.setAttribute('animation__leave',
      'property: scale; to: 1 1 1; dur: 200; startEvents: mouseleave');
    this.el.appendChild(icon);

    // 정보 패널 (초기에는 숨김)
    this.createInfoPanel();
  },

  createInfoPanel: function() {
    var panel = document.createElement('a-entity');
    panel.setAttribute('class', 'poi-panel');
    panel.setAttribute('visible', false);
    panel.setAttribute('position', '0 0.5 0');

    // 배경
    var bg = document.createElement('a-plane');
    bg.setAttribute('width', 1.2);
    bg.setAttribute('height', 0.8);
    bg.setAttribute('color', '#ffffff');
    bg.setAttribute('opacity', 0.95);
    panel.appendChild(bg);

    // 이미지 (있는 경우)
    if (this.data.imageUrl) {
      var img = document.createElement('a-image');
      img.setAttribute('src', this.data.imageUrl);
      img.setAttribute('width', 1);
      img.setAttribute('height', 0.5);
      img.setAttribute('position', '0 0.15 0.01');
      panel.appendChild(img);
    }

    // 제목
    var title = document.createElement('a-text');
    title.setAttribute('value', this.data.title);
    title.setAttribute('color', '#000000');
    title.setAttribute('width', 1);
    title.setAttribute('align', 'center');
    title.setAttribute('position', '0 0.3 0.01');
    title.setAttribute('font', 'roboto');
    panel.appendChild(title);

    // 설명
    var desc = document.createElement('a-text');
    desc.setAttribute('value', this.data.description);
    desc.setAttribute('color', '#333333');
    desc.setAttribute('width', 0.9);
    desc.setAttribute('wrap-count', 30);
    desc.setAttribute('position', '0 -0.2 0.01');
    panel.appendChild(desc);

    // 닫기 버튼
    var closeBtn = document.createElement('a-plane');
    closeBtn.setAttribute('width', 0.2);
    closeBtn.setAttribute('height', 0.2);
    closeBtn.setAttribute('color', '#f44336');
    closeBtn.setAttribute('position', '0.5 0.35 0.01');
    closeBtn.setAttribute('class', 'clickable');
    closeBtn.addEventListener('click', () => {
      panel.setAttribute('visible', false);
    });
    panel.appendChild(closeBtn);

    this.el.appendChild(panel);
    this.panel = panel;
  },

  createLinkMarker: function() {
    // 기존 <a-link> 스타일 유지
    var link = document.createElement('a-link');
    link.setAttribute('href', `/space/scene/${this.data.targetSceneId}`);
    link.setAttribute('title', this.data.title);
    link.setAttribute('class', 'clickable');
    this.el.appendChild(link);
  },

  setupInteractions: function() {
    var icon = this.el.querySelector('.poi-icon');
    if (icon) {
      icon.addEventListener('click', () => {
        this.panel.setAttribute('visible', !this.panel.getAttribute('visible'));
      });
    }
  }
});
```

### 2. responsive-panel.js (반응형 UI)
```javascript
AFRAME.registerComponent('responsive-panel', {
  schema: {
    minDistance: {type: 'number', default: 2},
    maxDistance: {type: 'number', default: 10},
    minScale: {type: 'number', default: 0.5},
    maxScale: {type: 'number', default: 1.5}
  },

  init: function() {
    this.camera = this.el.sceneEl.camera;
    // 항상 카메라를 향하도록
    this.el.setAttribute('look-at', '[camera]');
  },

  tick: function() {
    if (!this.camera) return;

    // 카메라와의 거리 계산
    var cameraPos = this.camera.parent.position;
    var panelPos = this.el.object3D.position;
    var distance = cameraPos.distanceTo(panelPos);

    // 거리에 비례한 스케일 계산
    var scale = this.calculateScale(distance);
    this.el.setAttribute('scale', `${scale} ${scale} ${scale}`);

    // 너무 가까우면 투명도 조정
    if (distance < 1) {
      var opacity = distance;  // 0~1
      this.el.setAttribute('opacity', opacity);
    }
  },

  calculateScale: function(distance) {
    var minDist = this.data.minDistance;
    var maxDist = this.data.maxDistance;
    var minScale = this.data.minScale;
    var maxScale = this.data.maxScale;

    // 선형 보간
    var ratio = (distance - minDist) / (maxDist - minDist);
    ratio = Math.max(0, Math.min(1, ratio));  // clamp [0,1]

    return minScale + (maxScale - minScale) * (1 - ratio);
  }
});
```

### 3. poi-editor.js (편집 모드)
```javascript
AFRAME.registerComponent('poi-editor', {
  schema: {
    enabled: {type: 'boolean', default: false},
    spaceId: {type: 'string'}
  },

  init: function() {
    this.raycaster = this.el.sceneEl.querySelector('[raycaster]');
    this.setupKeyboardControls();
    this.setupUI();
  },

  setupKeyboardControls: function() {
    window.addEventListener('keydown', (evt) => {
      if (!this.data.enabled) return;

      // 'I' 키: Info POI 추가
      if (evt.key === 'i') {
        this.addPOI('info');
      }

      // 'L' 키: Link POI 추가
      if (evt.key === 'l') {
        this.addPOI('link');
      }

      // 'E' 키: 편집 모드 토글
      if (evt.key === 'e') {
        this.toggleEditMode();
      }
    });
  },

  addPOI: function(type) {
    // Raycaster로 커서 위치 계산
    var intersection = this.raycaster.components.raycaster.intersections[0];
    if (!intersection) {
      console.warn('No intersection found');
      return;
    }

    var position = intersection.point;
    var cameraRotation = this.el.sceneEl.camera.rotation;

    // 모달 창 띄우기
    this.showPOIModal(type, position, cameraRotation);
  },

  showPOIModal: function(type, position, rotation) {
    // HTML 모달 생성
    var modal = document.createElement('div');
    modal.id = 'poi-modal';
    modal.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      z-index: 1000;
    `;

    modal.innerHTML = `
      <h3>POI 추가 (${type})</h3>
      <form id="poi-form">
        <label>제목: <input type="text" name="title" required></label><br>
        <label>설명: <textarea name="description" rows="3"></textarea></label><br>
        ${type === 'info' ?
          '<label>이미지: <input type="file" name="image" accept="image/*"></label><br>' :
          '<label>연결할 씬: <select name="target_scene"></select></label><br>'
        }
        <label>위치 X: <input type="number" name="x" value="${position.x.toFixed(2)}" step="0.1"></label><br>
        <label>위치 Y: <input type="number" name="y" value="${position.y.toFixed(2)}" step="0.1"></label><br>
        <label>위치 Z: <input type="number" name="z" value="${position.z.toFixed(2)}" step="0.1"></label><br>
        <button type="submit">저장</button>
        <button type="button" onclick="this.closest('#poi-modal').remove()">취소</button>
      </form>
    `;

    document.body.appendChild(modal);

    // 씬 목록 로드 (type === 'link'인 경우)
    if (type === 'link') {
      this.loadSceneList(modal.querySelector('select[name="target_scene"]'));
    }

    // 폼 제출 이벤트
    modal.querySelector('#poi-form').addEventListener('submit', (evt) => {
      evt.preventDefault();
      this.savePOI(type, new FormData(evt.target));
      modal.remove();
    });
  },

  loadSceneList: async function(selectEl) {
    try {
      const response = await fetch(`/space/scenes/${this.data.spaceId}`);
      const scenes = await response.json();

      scenes.forEach(scene => {
        const option = document.createElement('option');
        option.value = scene.id;
        option.textContent = scene.name;
        selectEl.appendChild(option);
      });
    } catch (err) {
      console.error('Failed to load scenes:', err);
    }
  },

  savePOI: async function(type, formData) {
    try {
      const response = await fetch('/space/poi/create', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        console.log('POI created:', result);

        // 씬에 POI 즉시 추가
        this.renderPOI(result.poi);
      }
    } catch (err) {
      console.error('Failed to save POI:', err);
    }
  },

  renderPOI: function(poiData) {
    var poi = document.createElement('a-entity');
    poi.setAttribute('poi-marker', {
      poiId: poiData.poi_id,
      type: poiData.type,
      title: poiData.title,
      description: poiData.description,
      imageUrl: poiData.image_url,
      targetSceneId: poiData.target_scene_id
    });
    poi.setAttribute('position', poiData.position);
    poi.setAttribute('rotation', poiData.rotation);
    poi.setAttribute('responsive-panel', '');

    this.el.sceneEl.appendChild(poi);
  },

  toggleEditMode: function() {
    this.data.enabled = !this.data.enabled;

    // UI 표시
    var editorUI = document.querySelector('#editor-ui');
    if (editorUI) {
      editorUI.setAttribute('visible', this.data.enabled);
    }

    console.log('Edit mode:', this.data.enabled ? 'ON' : 'OFF');
  },

  setupUI: function() {
    // VR 내부 UI
    var ui = document.createElement('a-entity');
    ui.id = 'editor-ui';
    ui.setAttribute('visible', false);
    ui.setAttribute('position', '0 2 -1.5');

    // Info 버튼
    var infoBtn = document.createElement('a-plane');
    infoBtn.setAttribute('width', 0.5);
    infoBtn.setAttribute('height', 0.2);
    infoBtn.setAttribute('color', '#4CAF50');
    infoBtn.setAttribute('position', '-0.3 0 0');
    infoBtn.setAttribute('class', 'clickable');
    var infoText = document.createElement('a-text');
    infoText.setAttribute('value', '+ Info');
    infoText.setAttribute('align', 'center');
    infoText.setAttribute('color', '#ffffff');
    infoText.setAttribute('position', '0 0 0.01');
    infoBtn.appendChild(infoText);
    infoBtn.addEventListener('click', () => this.addPOI('info'));
    ui.appendChild(infoBtn);

    // Link 버튼
    var linkBtn = document.createElement('a-plane');
    linkBtn.setAttribute('width', 0.5);
    linkBtn.setAttribute('height', 0.2);
    linkBtn.setAttribute('color', '#2196F3');
    linkBtn.setAttribute('position', '0.3 0 0');
    linkBtn.setAttribute('class', 'clickable');
    var linkText = document.createElement('a-text');
    linkText.setAttribute('value', '+ Link');
    linkText.setAttribute('align', 'center');
    linkText.setAttribute('color', '#ffffff');
    linkText.setAttribute('position', '0 0 0.01');
    linkBtn.appendChild(linkText);
    linkBtn.addEventListener('click', () => this.addPOI('link'));
    ui.appendChild(linkBtn);

    this.el.sceneEl.appendChild(ui);
  }
});
```

---

## 🔧 FastAPI 백엔드 구현

### 1. 스키마 정의 (schemas/poi_model.py)
```python
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, Literal
from fastapi import UploadFile

class Position(BaseModel):
    x: float
    y: float
    z: float

class Rotation(BaseModel):
    x: float = 0
    y: float = 0
    z: float = 0

class POIBase(BaseModel):
    type: Literal["info", "link", "media"]
    title: str
    description: Optional[str] = None
    position: Position
    rotation: Rotation = Field(default_factory=lambda: Rotation())
    visible: bool = True

class CreatePOIForm:
    def __init__(self, request: Request):
        self.request = request
        self.errors = []

    async def load_data(self):
        form = await self.request.form()
        self.type = form.get("type")
        self.title = form.get("title")
        self.description = form.get("description")
        self.x = float(form.get("x", 0))
        self.y = float(form.get("y", 0))
        self.z = float(form.get("z", 0))
        self.target_scene_id = form.get("target_scene_id")
        self.image = form.get("image")  # UploadFile

    async def is_valid(self):
        if not self.title:
            self.errors.append("Title is required")
        if self.type == "link" and not self.target_scene_id:
            self.errors.append("Target scene is required for link type")
        return len(self.errors) == 0

class POIInDB(POIBase):
    poi_id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    scene_id: ObjectId
    image_id: Optional[ObjectId] = None
    target_scene_id: Optional[ObjectId] = None
    created_at: datetime
    updated_at: datetime
```

### 2. 데이터베이스 메서드 (models/database.py 확장)
```python
class db_manager:
    # ... 기존 코드 ...

    @classmethod
    async def create_poi(cls, scene_id: ObjectId, poi_data: dict) -> ObjectId:
        """POI 생성"""
        poi_data['created_at'] = datetime.utcnow()
        poi_data['updated_at'] = datetime.utcnow()

        # 이미지 업로드 처리
        if 'image' in poi_data and poi_data['image']:
            image_id = await cls.store_image(
                poi_data['image'].filename,
                poi_data['image'].content_type,
                poi_data['image'].file
            )
            poi_data['image_id'] = image_id
            del poi_data['image']

        # POI를 씬의 pois 배열에 추가
        poi_id = ObjectId()
        poi_data['poi_id'] = poi_id

        await cls.get_collection('scenes').update_one(
            {'_id': scene_id},
            {'$push': {'pois': poi_data}}
        )

        return poi_id

    @classmethod
    async def update_poi(cls, scene_id: ObjectId, poi_id: ObjectId, poi_data: dict):
        """POI 업데이트"""
        poi_data['updated_at'] = datetime.utcnow()

        # 배열 내 특정 POI 업데이트
        update_fields = {
            f'pois.$.{key}': value
            for key, value in poi_data.items()
        }

        await cls.get_collection('scenes').update_one(
            {'_id': scene_id, 'pois.poi_id': poi_id},
            {'$set': update_fields}
        )

    @classmethod
    async def delete_poi(cls, scene_id: ObjectId, poi_id: ObjectId):
        """POI 삭제"""
        await cls.get_collection('scenes').update_one(
            {'_id': scene_id},
            {'$pull': {'pois': {'poi_id': poi_id}}}
        )

    @classmethod
    async def get_pois(cls, scene_id: ObjectId):
        """씬의 모든 POI 조회"""
        scene = await cls.get_collection('scenes').find_one(
            {'_id': scene_id},
            {'pois': 1}
        )
        return scene.get('pois', []) if scene else []
```

### 3. 라우터 (routers/poi.py)
```python
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId

from ..models.database import db_manager
from ..models.auth_manager import get_current_user
from ..schemas.poi_model import CreatePOIForm

router = APIRouter(include_in_schema=True)

@router.post("/space/poi/create/{scene_id}")
async def create_poi(
    request: Request,
    scene_id: str,
    auth_user = Depends(get_current_user)
):
    """POI 생성"""
    if not auth_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 권한 확인 (씬이 속한 공간의 Editor인지 확인)
    scene = await db_manager.get_scene(ObjectId(scene_id))
    space = await db_manager.get_space(scene['space_id'])  # space_id 필드 필요

    if str(auth_user.id) not in space.viewers or \
       space.viewers[str(auth_user.id)] != 'Editor':
        raise HTTPException(status_code=403, detail="No permission")

    # 폼 데이터 로드
    form = CreatePOIForm(request)
    await form.load_data()

    if not await form.is_valid():
        return JSONResponse(
            status_code=400,
            content={"errors": form.errors}
        )

    # POI 데이터 구성
    poi_data = {
        'type': form.type,
        'title': form.title,
        'description': form.description,
        'position': {'x': form.x, 'y': form.y, 'z': form.z},
        'rotation': {'x': 0, 'y': 0, 'z': 0},
        'visible': True,
        'image': form.image,
        'target_scene_id': ObjectId(form.target_scene_id) if form.target_scene_id else None
    }

    # POI 생성
    poi_id = await db_manager.create_poi(ObjectId(scene_id), poi_data)

    return JSONResponse(
        status_code=201,
        content={
            "success": True,
            "poi_id": str(poi_id),
            "message": "POI created successfully"
        }
    )

@router.put("/space/poi/update/{scene_id}/{poi_id}")
async def update_poi(
    request: Request,
    scene_id: str,
    poi_id: str,
    auth_user = Depends(get_current_user)
):
    """POI 업데이트"""
    if not auth_user:
        raise HTTPException(status_code=401)

    form = CreatePOIForm(request)
    await form.load_data()

    if not await form.is_valid():
        return JSONResponse(status_code=400, content={"errors": form.errors})

    poi_data = {
        'title': form.title,
        'description': form.description,
        'position': {'x': form.x, 'y': form.y, 'z': form.z}
    }

    await db_manager.update_poi(
        ObjectId(scene_id),
        ObjectId(poi_id),
        poi_data
    )

    return JSONResponse(content={"success": True})

@router.delete("/space/poi/delete/{scene_id}/{poi_id}")
async def delete_poi(
    scene_id: str,
    poi_id: str,
    auth_user = Depends(get_current_user)
):
    """POI 삭제"""
    if not auth_user:
        raise HTTPException(status_code=401)

    await db_manager.delete_poi(ObjectId(scene_id), ObjectId(poi_id))

    return JSONResponse(content={"success": True})

@router.get("/space/pois/{scene_id}")
async def get_pois(
    scene_id: str,
    auth_user = Depends(get_current_user)
):
    """씬의 모든 POI 조회"""
    if not auth_user:
        raise HTTPException(status_code=401)

    pois = await db_manager.get_pois(ObjectId(scene_id))

    # ObjectId를 문자열로 변환
    for poi in pois:
        poi['poi_id'] = str(poi['poi_id'])
        if 'image_id' in poi and poi['image_id']:
            poi['image_url'] = f"/asset/image/{poi['image_id']}"
        if 'target_scene_id' in poi and poi['target_scene_id']:
            poi['target_scene_id'] = str(poi['target_scene_id'])

    return JSONResponse(content={"pois": pois})

@router.get("/space/scenes/{space_id}")
async def get_scenes_for_linking(
    space_id: str,
    auth_user = Depends(get_current_user)
):
    """링크 생성을 위한 씬 목록"""
    if not auth_user:
        raise HTTPException(status_code=401)

    scenes = await db_manager.get_scenes_from_space(ObjectId(space_id))

    return JSONResponse(content={
        "scenes": [
            {"id": str(scene_id), "name": scene_name}
            for scene_id, scene_name in scenes
        ]
    })
```

### 4. main.py에 라우터 등록
```python
# main.py
from app.core.routers import page_view, register, login, create, space, asset, poi

# ...

app.include_router(poi.router, prefix="", tags=["poi"])
```

---

## 🎨 사용자 입력 UI (모달 창)

### 1. HTML/CSS 모달 컴포넌트 (static/css/poi-modal.css)
```css
/* POI 모달 스타일 */
#poi-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

#poi-modal {
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.poi-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.poi-modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.poi-modal-close {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  transition: color 0.2s;
}

.poi-modal-close:hover {
  color: #333;
}

.poi-form-group {
  margin-bottom: 20px;
}

.poi-form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
}

.poi-form-group input[type="text"],
.poi-form-group textarea,
.poi-form-group select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.poi-form-group input:focus,
.poi-form-group textarea:focus,
.poi-form-group select:focus {
  outline: none;
  border-color: #4CAF50;
}

.poi-form-group textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

/* 이미지 업로드 영역 */
.poi-image-upload {
  border: 3px dashed #d0d0d0;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.poi-image-upload:hover {
  border-color: #4CAF50;
  background: #f0f8f0;
}

.poi-image-upload.dragover {
  border-color: #4CAF50;
  background: #e8f5e9;
}

.poi-image-preview {
  margin-top: 15px;
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  display: none;
}

.poi-image-preview.show {
  display: block;
}

/* 좌표 입력 그리드 */
.poi-coordinates {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.poi-coordinates input {
  width: 100%;
}

/* 버튼 그룹 */
.poi-button-group {
  display: flex;
  gap: 10px;
  margin-top: 25px;
}

.poi-btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.poi-btn-primary {
  background: #4CAF50;
  color: white;
}

.poi-btn-primary:hover {
  background: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.poi-btn-secondary {
  background: #f5f5f5;
  color: #333;
}

.poi-btn-secondary:hover {
  background: #e0e0e0;
}

.poi-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 탭 스타일 */
.poi-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.poi-tab {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #999;
  position: relative;
  transition: color 0.2s;
}

.poi-tab.active {
  color: #4CAF50;
}

.poi-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #4CAF50;
}

/* 도움말 텍스트 */
.poi-help-text {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

/* 로딩 상태 */
.poi-loading {
  display: none;
  text-align: center;
  padding: 20px;
}

.poi-loading.show {
  display: block;
}

.poi-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4CAF50;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### 2. 모달 창 JavaScript (poi-editor.js 개선)
```javascript
// 기존 showPOIModal 함수를 대체
showPOIModal: function(type, position, rotation) {
  // 오버레이 생성
  const overlay = document.createElement('div');
  overlay.id = 'poi-modal-overlay';

  // 모달 컨테이너
  const modal = document.createElement('div');
  modal.id = 'poi-modal';

  // 모달 HTML 구조
  modal.innerHTML = `
    <div class="poi-modal-header">
      <h3>${type === 'info' ? '📍 정보 POI 추가' : '🔗 링크 POI 추가'}</h3>
      <button class="poi-modal-close" type="button">&times;</button>
    </div>

    <form id="poi-form" enctype="multipart/form-data">
      <!-- POI 타입 (hidden) -->
      <input type="hidden" name="type" value="${type}">
      <input type="hidden" name="scene_id" value="${this.data.sceneId}">

      <!-- 기본 정보 -->
      <div class="poi-form-group">
        <label for="poi-title">제목 *</label>
        <input type="text"
               id="poi-title"
               name="title"
               placeholder="예: 역사적 건물"
               required
               maxlength="50">
        <div class="poi-help-text">최대 50자</div>
      </div>

      <div class="poi-form-group">
        <label for="poi-description">설명</label>
        <textarea id="poi-description"
                  name="description"
                  placeholder="이곳에 대한 자세한 설명을 입력하세요..."
                  maxlength="500"></textarea>
        <div class="poi-help-text">최대 500자</div>
      </div>

      ${type === 'info' ? `
        <!-- 이미지 업로드 (Info POI만) -->
        <div class="poi-form-group">
          <label>이미지 (선택)</label>
          <div class="poi-image-upload" id="poi-image-dropzone">
            <input type="file"
                   id="poi-image"
                   name="image"
                   accept="image/jpeg,image/png,image/webp"
                   style="display:none">
            <div class="poi-upload-prompt">
              <p>📷 클릭하거나 이미지를 드래그하세요</p>
              <small>JPG, PNG, WEBP (최대 5MB)</small>
            </div>
            <img id="poi-image-preview" class="poi-image-preview" alt="미리보기">
          </div>
          <div class="poi-help-text">이미지는 1:1 비율 권장 (예: 512x512)</div>
        </div>
      ` : `
        <!-- 연결할 씬 선택 (Link POI만) -->
        <div class="poi-form-group">
          <label for="poi-target-scene">연결할 공간 *</label>
          <select id="poi-target-scene" name="target_scene_id" required>
            <option value="">-- 선택하세요 --</option>
          </select>
          <div class="poi-help-text">이 링크를 클릭하면 선택한 공간으로 이동합니다</div>
        </div>
      `}

      <!-- 위치 좌표 -->
      <div class="poi-form-group">
        <label>위치 좌표</label>
        <div class="poi-coordinates">
          <div>
            <label for="poi-x">X</label>
            <input type="number"
                   id="poi-x"
                   name="x"
                   value="${position.x.toFixed(2)}"
                   step="0.1"
                   required>
          </div>
          <div>
            <label for="poi-y">Y</label>
            <input type="number"
                   id="poi-y"
                   name="y"
                   value="${position.y.toFixed(2)}"
                   step="0.1"
                   required>
          </div>
          <div>
            <label for="poi-z">Z</label>
            <input type="number"
                   id="poi-z"
                   name="z"
                   value="${position.z.toFixed(2)}"
                   step="0.1"
                   required>
          </div>
        </div>
        <div class="poi-help-text">
          현재 보고 있는 방향의 좌표입니다.
          <a href="#" id="recalculate-position">현재 위치 재계산</a>
        </div>
      </div>

      <!-- 버튼 -->
      <div class="poi-button-group">
        <button type="button" class="poi-btn poi-btn-secondary" id="poi-cancel">
          취소
        </button>
        <button type="submit" class="poi-btn poi-btn-primary" id="poi-submit">
          ${type === 'info' ? '정보 추가' : '링크 생성'}
        </button>
      </div>

      <!-- 로딩 상태 -->
      <div class="poi-loading" id="poi-loading">
        <div class="poi-spinner"></div>
        <p>저장 중...</p>
      </div>
    </form>
  `;

  overlay.appendChild(modal);
  document.body.appendChild(overlay);

  // 이벤트 리스너 설정
  this.setupModalEvents(overlay, modal, type, position, rotation);

  // 링크 타입이면 씬 목록 로드
  if (type === 'link') {
    this.loadSceneList(modal.querySelector('#poi-target-scene'));
  }
},

setupModalEvents: function(overlay, modal, type, position, rotation) {
  const form = modal.querySelector('#poi-form');
  const closeBtn = modal.querySelector('.poi-modal-close');
  const cancelBtn = modal.querySelector('#poi-cancel');
  const imageInput = modal.querySelector('#poi-image');
  const imageDropzone = modal.querySelector('#poi-image-dropzone');
  const imagePreview = modal.querySelector('#poi-image-preview');
  const recalcBtn = modal.querySelector('#recalculate-position');

  // 닫기 버튼
  const closeModal = () => overlay.remove();
  closeBtn?.addEventListener('click', closeModal);
  cancelBtn?.addEventListener('click', closeModal);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal();
  });

  // 이미지 업로드 (드래그 앤 드롭)
  if (imageDropzone) {
    imageDropzone.addEventListener('click', () => imageInput.click());

    imageDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      imageDropzone.classList.add('dragover');
    });

    imageDropzone.addEventListener('dragleave', () => {
      imageDropzone.classList.remove('dragover');
    });

    imageDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      imageDropzone.classList.remove('dragover');

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        imageInput.files = files;
        this.previewImage(files[0], imagePreview);
      }
    });

    imageInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        this.previewImage(e.target.files[0], imagePreview);
      }
    });
  }

  // 위치 재계산
  recalcBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    const newPos = this.getCurrentCursorPosition();
    if (newPos) {
      modal.querySelector('#poi-x').value = newPos.x.toFixed(2);
      modal.querySelector('#poi-y').value = newPos.y.toFixed(2);
      modal.querySelector('#poi-z').value = newPos.z.toFixed(2);
    }
  });

  // 폼 제출
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = modal.querySelector('#poi-submit');
    const loading = modal.querySelector('#poi-loading');

    // 로딩 상태
    submitBtn.disabled = true;
    loading.classList.add('show');

    try {
      await this.savePOI(type, new FormData(form));
      closeModal();
    } catch (err) {
      alert('POI 저장에 실패했습니다: ' + err.message);
    } finally {
      submitBtn.disabled = false;
      loading.classList.remove('show');
    }
  });
},

previewImage: function(file, previewEl) {
  // 파일 크기 체크 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('이미지 크기는 5MB 이하여야 합니다.');
    return;
  }

  // 미리보기
  const reader = new FileReader();
  reader.onload = (e) => {
    previewEl.src = e.target.result;
    previewEl.classList.add('show');
  };
  reader.readAsDataURL(file);
},

getCurrentCursorPosition: function() {
  const intersection = this.raycaster.components.raycaster.intersections[0];
  return intersection ? intersection.point : null;
}
```

### 3. 모바일 최적화 버전
```css
/* 모바일 대응 */
@media (max-width: 768px) {
  #poi-modal {
    width: 95%;
    padding: 20px;
    max-height: 90vh;
  }

  .poi-modal-header h3 {
    font-size: 20px;
  }

  .poi-coordinates {
    grid-template-columns: 1fr;
  }

  .poi-button-group {
    flex-direction: column;
  }

  .poi-btn {
    width: 100%;
  }
}
```

---

## 🎨 프론트엔드 템플릿 수정

### scene.html 업데이트 (CSS 추가)
```html
{% extends "base.html" %}
{% block title %}Simulverse Management System{%endblock %}

{% block head %}
{{ super() }}
<!-- POI 모달 CSS 추가 -->
<link rel="stylesheet" href="{{ url_for('static', path='/css/poi-modal.css') }}">
<!-- A-Frame 및 스크립트 -->
<script src="https://aframe.io/releases/1.6.0/aframe.min.js"></script>

{% block head %}
{{ super() }}
<script src="https://aframe.io/releases/1.6.0/aframe.min.js"></script>
<script src="https://unpkg.com/aframe-event-set-component@5/dist/aframe-event-set-component.min.js"></script>
<script src="https://unpkg.com/aframe-look-at-component@1.0.0/dist/aframe-look-at-component.min.js"></script>
<script src="{{ url_for('static', path='/scripts/link-controls.js') }}"></script>
<script src="{{ url_for('static', path='/scripts/contents-save.js') }}"></script>
<!-- 신규 POI 스크립트 -->
<script src="{{ url_for('static', path='/scripts/poi-marker.js') }}"></script>
<script src="{{ url_for('static', path='/scripts/responsive-panel.js') }}"></script>
<script src="{{ url_for('static', path='/scripts/poi-editor.js') }}"></script>
{% endblock %}

{% block page_content %}
<main role="main" class="container">
  <div class="row" style="height: 75vh;">
    <a-scene embedded>
      <a-assets>
        <img id="background" src="/asset/image/{{data.background}}">
      </a-assets>

      <!-- 360도 배경 -->
      <a-sky id="image-360" radius="10" src="#background"></a-sky>

      <!-- 기존 링크 -->
      {% for link in data.links %}
      <a-link class="clickable"
              title="{{link[0]}}"
              href="/space/scene/{{data.space_id}}/{{link[1]}}"
              origin="{{link[8]}}"
              position="{{link[2]}} {{link[3]}} {{link[4]}}"
              rotation="{{link[5]}} {{link[6]}} {{link[7]}}"></a-link>
      {% endfor %}

      <!-- 새로운 POI 시스템 -->
      {% for poi in data.pois %}
      <a-entity poi-marker="
                  poiId: {{poi.poi_id}};
                  type: {{poi.type}};
                  title: {{poi.title}};
                  description: {{poi.description}};
                  {% if poi.image_url %}imageUrl: {{poi.image_url}};{% endif %}
                  {% if poi.target_scene_id %}targetSceneId: {{poi.target_scene_id}};{% endif %}"
                position="{{poi.position.x}} {{poi.position.y}} {{poi.position.z}}"
                rotation="{{poi.rotation.x}} {{poi.rotation.y}} {{poi.rotation.z}}"
                responsive-panel>
      </a-entity>
      {% endfor %}

      <!-- 저장 버튼 (기존) -->
      <a-box class="clickable"
             contents-save="space_id:{{data.space_id}}"
             height="0.5" width="0.5"
             position="0 -2 -2"
             color="red"></a-box>

      <!-- 카메라 + 커서 + 편집 모드 -->
      <a-camera poi-editor="enabled: {{data.role == 'Editor'}}; spaceId: {{data.space_id}}">
        <a-cursor raycaster="objects: .clickable, a-sky"></a-cursor>
      </a-camera>
    </a-scene>
  </div>

  <!-- 편집 모드 안내 (데스크톱) -->
  {% if data.role == 'Editor' %}
  <div class="alert alert-info mt-3">
    <strong>편집 모드:</strong>
    [E] 편집 모드 토글 |
    [I] Info POI 추가 |
    [L] Link POI 추가
  </div>
  {% endif %}
</main>
{% endblock %}
```

---

## 📝 구현 체크리스트

### Phase 1: DB 스키마 및 백엔드 (2일)
- [ ] `schemas/poi_model.py` 생성
- [ ] `database.py`에 POI 관련 메서드 추가
  - [ ] `create_poi()`
  - [ ] `update_poi()`
  - [ ] `delete_poi()`
  - [ ] `get_pois()`
- [ ] `routers/poi.py` 생성
  - [ ] POST `/space/poi/create/{scene_id}`
  - [ ] PUT `/space/poi/update/{scene_id}/{poi_id}`
  - [ ] DELETE `/space/poi/delete/{scene_id}/{poi_id}`
  - [ ] GET `/space/pois/{scene_id}`
  - [ ] GET `/space/scenes/{space_id}` (링크용)
- [ ] MongoDB 마이그레이션 스크립트
  - [ ] scenes에 `pois: []` 필드 추가
- [ ] 권한 검증 로직 추가
- [ ] 단위 테스트 작성

### Phase 1.5: 사용자 입력 UI (모달 창) (1일)
- [ ] `static/css/poi-modal.css` 생성
  - [ ] 모달 오버레이 및 컨테이너 스타일
  - [ ] 폼 입력 필드 스타일
  - [ ] 이미지 업로드 드래그 앤 드롭 영역
  - [ ] 버튼 및 로딩 애니메이션
  - [ ] 모바일 반응형 디자인
- [ ] `poi-editor.js`에 모달 창 기능 추가
  - [ ] `showPOIModal()` - 완전한 HTML 구조
  - [ ] `setupModalEvents()` - 모든 이벤트 핸들러
  - [ ] `previewImage()` - 이미지 미리보기 + 크기 검증
  - [ ] `getCurrentCursorPosition()` - 좌표 재계산
  - [ ] 드래그 앤 드롭 이미지 업로드
  - [ ] 폼 검증 (제목 필수, 이미지 크기 등)
- [ ] 모달 창 기능 테스트
  - [ ] Info POI 모달 (이미지 + 설명)
  - [ ] Link POI 모달 (씬 선택)
  - [ ] 드래그 앤 드롭 동작
  - [ ] 이미지 미리보기
  - [ ] 좌표 재계산 버튼
  - [ ] 로딩 상태 표시

### Phase 2: A-Frame 컴포넌트 (2-3일)
- [ ] `static/scripts/poi-marker.js` 구현
  - [ ] Info 마커 렌더링
  - [ ] Link 마커 렌더링
  - [ ] 인터랙션 (클릭 시 패널 표시)
- [ ] `static/scripts/responsive-panel.js` 구현
  - [ ] 거리 기반 스케일 조정
  - [ ] Look-at 카메라
  - [ ] 투명도 조정
- [ ] `static/scripts/poi-editor.js` 구현
  - [ ] 키보드 단축키 (I, L, E)
  - [ ] 모달 창 생성
  - [ ] Raycaster 교차점 계산
  - [ ] 서버 통신 (fetch API)
  - [ ] 실시간 POI 렌더링
- [ ] VR 컨트롤러 지원 (선택)
- [ ] 드래그 앤 드롭 위치 조정 (선택)

### Phase 3: 템플릿 및 UI (1일)
- [ ] `scene.html` 수정
  - [ ] POI 렌더링 루프 추가
  - [ ] 스크립트 import
  - [ ] 편집 모드 안내 추가
- [ ] CSS 스타일링
  - [ ] 모달 창 디자인
  - [ ] 편집 모드 UI
- [ ] 반응형 디자인 (모바일)

### Phase 4: 테스트 및 최적화 (1-2일)
- [ ] 기능 테스트
  - [ ] Info POI 추가/수정/삭제
  - [ ] Link POI 추가/수정/삭제
  - [ ] 권한 검증
  - [ ] 이미지 업로드
- [ ] 성능 테스트
  - [ ] 20개 이상 POI 렌더링
  - [ ] 모바일 성능
  - [ ] VR 헤드셋 테스트
- [ ] 버그 수정
- [ ] 사용자 매뉴얼 작성

---

## 🚀 배포 전략

### 1단계: 베타 기능으로 출시
```python
# config.py
FEATURE_FLAGS = {
    "poi_system": True,  # 베타 기능 활성화
    "poi_editor": True   # 편집 모드
}

# space.py
if config.FEATURE_FLAGS["poi_system"]:
    pois = await db_manager.get_pois(scene_id)
else:
    pois = []
```

### 2단계: 점진적 롤아웃
- 내부 테스터 → 일부 사용자 → 전체 사용자

### 3단계: 모니터링
- POI 생성 횟수
- 평균 POI 개수/씬
- 에러율
- 성능 메트릭

---

## 📊 예상 성능 영향

### 긍정적 영향
- 사용자 경험 대폭 향상
- 콘텐츠 풍부도 증가
- 교육/관광 활용도 증가

### 주의 사항
- POI 20개 초과 시 성능 저하 가능 → 제한 필요
- 이미지 크기 제한 (최대 5MB)
- 동시 편집 충돌 방지

---

## 🎯 성공 지표

### 기능 완성도
- ✅ Info POI 추가/수정/삭제 100% 작동
- ✅ Link POI 자유 배치 100% 작동
- ✅ 편집 모드 직관적 사용
- ✅ 반응형 UI 모든 기기에서 작동

### 성능
- ✅ POI 10개: 60fps 유지
- ✅ POI 20개: 30fps 이상
- ✅ 모바일: 30fps 이상

### 사용성
- ✅ POI 추가 시간 < 30초
- ✅ 사용자 설명서 없이 사용 가능
- ✅ 에러율 < 1%

---

**예상 완료**: 6-8일
**다음 단계**: Phase 1 (DB 스키마) 시작
