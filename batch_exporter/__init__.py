import os
from posixpath import dirname
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    PointerProperty
)

bl_info = {
    "name": "バッチエクスポーター",
    "author": "kazuya seto",
    "version": (1, 2),
    "blender": (2, 93, 0),
    "location": "3Dビューポート > Sidebar",
    "description": "指定のコレクション内のメッシュをそれぞれ書き出すアドオン",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

class MODELBATCHEXPORTER_OT_MeshExporter(bpy.types.Operator,ExportHelper):
    bl_idname = "object.modelbatchexporter_meshexporter"
    bl_label = "Export Mesh"
    bl_description = "メッシュとまとめて出力する"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = " [出力フォルダを選択]"

    def execute(self, context):
        basedir = os.path.dirname(self.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")

        view_layer = bpy.context.view_layer
        obj_active = view_layer.objects.active
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        
        # メッシュのオブジェクトを取得
        objs = [obj for obj in context.scene.targetcollection.objects
            if obj.type == "MESH"]
        for obj in objs:
            print(obj)
            exportmeshfbx(basedir=basedir,obj=obj)

        view_layer.objects.active = obj_active
        for obj in selection:
            obj.select_set(True)
        return {'FINISHED'}

# Sidebarのタブ [カスタムタブ] に、パネル [カスタムパネル] を追加
class MODELBATCHEXPORTER_PT_CustomPanel(bpy.types.Panel):
    bl_label = "モデル書き出す君"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "書き出し"
    bl_context = "objectmode"

    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PLUGIN')

    # メニューの描画処理
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # ボタンを追加
        layout.label(text="指定のコレクション内のメッシュを全て書き出す")
        layout.label(text="座標は原点、スケールは1、回転は0にします。")
        layout.separator()
        layout.prop(scene, "targetcollection")
        layout.separator()
        layout.operator(MODELBATCHEXPORTER_OT_MeshExporter.bl_idname, text="すべて書き出し")

classes = {
    MODELBATCHEXPORTER_OT_MeshExporter,
    MODELBATCHEXPORTER_PT_CustomPanel
}

# FBXの書き出し
def exportmeshfbx(basedir, obj):
    obj.select_set(True)
    view_layer = bpy.context.view_layer
    view_layer.objects.active = obj
    origine = obj.matrix_world.copy()
    init_transform(obj)
    name = bpy.path.clean_name(obj.name)
    fn = os.path.join(basedir, name)
    bpy.ops.export_scene.fbx(
        filepath=fn + ".fbx",
        use_selection=True,
        apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=True)
    obj.matrix_world = origine
    obj.select_set(False)
    print("バッチエクスポーター: 指定コレクション以下のメッシュがそれぞれのFBXファイルで書き出されました")

def init_transform(obj):
    obj.matrix_world.translation = (0, 0, 0)
    obj.rotation_euler = ( 0, 0, 0 )
    obj.scale = ( 1.0, 1.0, 1.0 )


# プロパティの初期化
def init_props():
    scene = bpy.types.Scene
    scene.targetcollection = PointerProperty(name="ターゲット", type=bpy.types.Collection)

# プロパティを削除
def clear_props():
    scene = bpy.types.Scene
    del scene.targetcollection

# 有効化
def register():
    for c in classes:
        bpy.utils.register_class(c)
    init_props()
    print("バッチエクスポーター: アドオン『バッチエクスポーター』が有効化されました。")

# 無効化
def unregister():
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)
    print("バッチエクスポーター: アドオン『バッチエクスポーター』が無効化されました。")

# メイン
if __name__ == "__main__":
    register()