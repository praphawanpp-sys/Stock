import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบจัดการสต็อกวัตถุดิบ (Food Cost Stock)",
    layout="wide",
)

# จำลองฐานข้อมูลสินค้า (จำลองจากโครงสร้างที่คุณมี)
if "inventory" not in st.session_state:
  st.session_state.inventory = pd.DataFrame({
      "SKU": ["SUP-001", "SUP-002", "SUP-003"],
      "Item Name (TH/EN)": [
          "อกไก่ (Chicken Breast)",
          "หมูสับ (Minced Pork)",
          "น้ำมันพืช (Vegetable Oil)",
      ],
      "Unit": ["Kg.", "Kg.", "Bottle"],
      "Price": [120.0, 150.0, 55.0],
      "Stock Balance": [50.0, 30.0, 10.0],
  })

st.title("ระบบจัดการสต็อกวัตถุดิบ (Food Cost Stock)")

# เมนูด้านข้าง (Sidebar)
menu = st.selectbox(
    "เลือกเมนูการใช้งาน",
    [
        "📊 หน้าแรก / สรุปภาพรวม",
        "📦 จัดการรายการสินค้า (Master)",
        "📥 บันทึกรับเข้า / เบิกออก (Transactions)",
    ],
)

# ---------------------------------------------------------
# เมนูที่ 1: หน้าแรก / สรุปภาพรวม
# ---------------------------------------------------------
if menu == "📊 หน้าแรก / สรุปภาพรวม":
  st.header("ภาพรวมสต็อกสินค้าคงเหลือ")

  df = st.session_state.inventory

  # คำนวณมูลค่ารวม
  df["Total Value"] = df["Stock Balance"] * df["Price"]
  total_investment = df["Total Value"].sum()

  col1, col2 = st.columns(2)
  with col1:
    st.metric(
        label="จำนวนรายการวัตถุดิบทั้งหมด", value=f"{len(df)} รายการ"
    )
  with col2:
    st.metric(
        label="มูลค่าสต็อกคงเหลือรวม", value=f"{total_investment:,.2f} บาท"
    )

  st.subheader("ตารางแสดงรายการสินค้าปัจจุบัน")
  st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# เมนูที่ 2: จัดการรายการสินค้า (Product Master)
# ---------------------------------------------------------
elif menu == "📦 จัดการรายการสินค้า (Master)":
  st.header("เพิ่ม / แก้ไข รายการวัตถุดิบ")

  with st.form("add_product_form"):
    st.subheader("เพิ่มสินค้าใหม่")
    new_sku = st.text_input("รหัสสินค้า (SKU / Sup Code)")
    new_name = st.text_input("ชื่อวัตถุดิบ (ไทย / อังกฤษ)")
    new_unit = st.text_input("หน่วยนับ (เช่น Kg., Pack, Pcs.)")
    new_price = st.number_input("ราคาต่อหน่วย (บาท)", min_value=0.0, step=0.1)
    new_stock = st.number_input("ยอดสต็อกเริ่มต้น", min_value=0.0, step=0.1)

    submit_button = st.form_submit_button(label="บันทึกสินค้าใหม่")

    if submit_button:
      if new_sku and new_name:
        new_row = pd.DataFrame({
            "SKU": [new_sku],
            "Item Name (TH/EN)": [new_name],
            "Unit": [new_unit],
            "Price": [new_price],
            "Stock Balance": [new_stock],
        })
        st.session_state.inventory = pd.concat(
            [st.session_state.inventory, new_row], ignore_index=True
        )
        st.success(f"เพิ่มวัตถุดิบ '{new_name}' สำเร็จเรียบร้อยแล้ว!")
      else:
        st.error("กรุณากรอกรหัสสินค้าและชื่อสินค้าให้ครบถ้วน")

  st.subheader("รายการสินค้าทั้งหมดในระบบ")
  st.dataframe(st.session_state.inventory, use_container_width=True)

# ---------------------------------------------------------
# เมนูที่ 3: บันทึกรับเข้า / เบิกออก (Transactions)
# ---------------------------------------------------------
elif menu == "📥 บันทึกรับเข้า / เบิกออก (Transactions)":
  st.header("บันทึกการเคลื่อนไหวสต็อก (Stock In / Out)")

  df = st.session_state.inventory

  if len(df) > 0:
    selected_item = st.selectbox(
        "เลือกวัตถุดิบ", df["Item Name (TH/EN)"].tolist()
    )
    action_type = st.radio(
        "ประเภทรายการ", ["รับเข้า (Stock In)", "เบิกออก / ใช้ไป (Stock Out)"]
    )
    qty_change = st.number_input("จำนวน", min_value=0.1, step=0.1)

    if st.button("ยืนยันการทำรายการ"):
      idx = df[df["Item Name (TH/EN)"].endswith(selected_item)].index[0]
      current_stock = df.loc[idx, "Stock Balance"]

      if action_type == "รับเข้า (Stock In)":
        st.session_state.inventory.loc[idx, "Stock Balance"] = (
            current_stock + qty_change
        )
        st.success(
            f"รับเข้า {selected_item} จำนวน {qty_change} สำเร็จ! ยอดคงเหลือใหม่:"
            f" {st.session_state.inventory.loc[idx, 'Stock Balance']}"
        )
      else:
        if current_stock >= qty_change:
          st.session_state.inventory.loc[idx, "Stock Balance"] = (
              current_stock - qty_change
          )
          st.success(
              f"เบิกออก {selected_item} จำนวน {qty_change} สำเร็จ! ยอดคงเหลือใหม่:"
              f" {st.session_state.inventory.loc[idx, 'Stock Balance']}"
          )
        else:
          st.error("สต็อกคงเหลือไม่พอสำหรับการเบิกออก!")
  else:
    st.warning("ยังไม่มีรายการสินค้า กรุณาเพิ่มสินค้าในเมนูก่อนครับ")
