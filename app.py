from datetime import datetime
import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบจัดการสต็อกวัตถุดิบ (Food Cost & Multi-Company)",
    layout="wide",
)

# รายชื่อบริษัทและสาขาตามโครงสร้างนิติบุคคล
companies = [
    "Daddy Deli (Head Office)",
    "Harvest Cafe (Branch 0001)",
    "Taboo By Daddy Deli (Branch 0002)",
    "Daddy Deli Pattaya Group (Head Office)",
    "Harvest Bakery And Restaurant (Head Office)",
    "Daddy Deli Beach House (Head Office)",
]

# หมวดหมู่วัตถุดิบ
categories = [
    "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others",
    "ผักและผลไม้ / Vegetables & Fruits",
    "ทะเล / Seafood",
    "เนื้อวัว / Beef",
    "น้ำผลไม้/Soft Drink/อื่นๆ / Juice/Soft Drink/Other",
    "เบียร์ / Beer",
    "เนื้อแกะ / Lamb",
    "ไวน์ / Wine",
    "ขนมปัง / Bread",
    "ของหวาน / Dessert",
    "เมล็ดกาแฟ / Coffee Beans",
]

# สร้างฐานข้อมูลจำลองแยกตามบริษัทใน session_state
if "company_inventories" not in st.session_state:
  st.session_state.company_inventories = {}
  for comp in companies:
    st.session_state.company_inventories[comp] = pd.DataFrame(
        columns=[
            "Product Code",
            "Item Name",
            "Category",
            "Unit",
            "Stock Balance",
            "Last Price",
        ]
    )
    if "Daddy Deli (Head Office)" in comp:
      st.session_state.company_inventories[comp] = pd.DataFrame({
          "Product Code": ["SUP-001", "SUP-002"],
          "Item Name": ["อกไก่ (Chicken Breast)", "น้ำมันพืช (Vegetable Oil)"],
          "Category": [
              "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others",
              "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others",
          ],
          "Unit": ["Kg.", "Bottle"],
          "Stock Balance": [50.0, 10.0],
          "Last Price": [120.0, 55.0],
      })

if "transactions" not in st.session_state:
  st.session_state.transactions = pd.DataFrame(
      columns=[
          "Company",
          "Date",
          "Supplier",
          "Item Name",
          "Quantity",
          "Price/Unit",
          "Vat Type",
          "Total Price",
      ]
  )

# --- ส่วนหัวของเว็บ ---
st.title("🍽️ ระบบจัดการสต็อกวัตถุดิบ (Food Cost Control)")

# 1. ย้าย "เลือกบริษัท / สาขา" มาไว้ที่ Sidebar (เมนูด้านข้าง)
selected_company = st.sidebar.selectbox(
    "🏢 กรุณาเลือกบริษัท / สาขา:", companies
)

st.sidebar.markdown("---")

# 2. ย้าย "เลือกเมนูการใช้งาน" มาไว้ที่หน้าจอหลัก (Main Screen)
menu = st.selectbox(
    "📌 เลือกเมนูการใช้งาน",
    [
        "📊 หน้าแรก / สรุปภาพรวม",
        "📦 จัดการรายการสินค้า (Master)",
        "📥 บันทึกรับเข้าสินค้า (Stock In)",
        "📜 ประวัติการรับสินค้า",
    ],
)

st.markdown("---")

# ดึงข้อมูลของบริษัทที่ถูกเลือกปัจจุบัน
current_inv = st.session_state.company_inventories[selected_company]

# ---------------------------------------------------------
# เมนูที่ 1: หน้าแรก / สรุปภาพรวม
# ---------------------------------------------------------
if menu == "📊 หน้าแรก / สรุปภาพรวม":
  st.header(f"ภาพรวมสต็อก: {selected_company}")

  if len(current_inv) > 0:
    current_inv["Total Value"] = (
        current_inv["Stock Balance"] * current_inv["Last Price"]
    )
    total_investment = current_inv["Total Value"].sum()

    col1, col2 = st.columns(2)
    with col1:
      st.metric(
          label="จำนวนรายการวัตถุดิบทั้งหมด",
          value=f"{len(current_inv)} รายการ",
      )
    with col2:
      st.metric(
          label="มูลค่าสต็อกคงเหลือรวม (ประมาณการ)",
          value=f"{total_investment:,.2f} บาท",
      )

    st.subheader("ตารางแสดงรายการสินค้าปัจจุบัน")
    st.dataframe(current_inv, use_container_width=True)
  else:
    st.info(
        f"ยังไม่มีข้อมูลสินค้าใน {selected_company} กรุณาเพิ่มสินค้าที่เมนู 'จัดการรายการสินค้า'"
    )

# ---------------------------------------------------------
# เมนูที่ 2: จัดการรายการสินค้า (Product Master)
# ---------------------------------------------------------
elif menu == "📦 จัดการรายการสินค้า (Master)":
  st.header(f"จัดการรายการวัตถุดิบ: {selected_company}")

  with st.form("add_product_form", clear_on_submit=True):
    st.subheader("➕ เพิ่มวัตถุดิบใหม่")
    col1, col2 = st.columns(2)
    with col1:
      new_code = st.text_input("รหัสสินค้า (Product Code)")
      new_name = st.text_input("ชื่อวัตถุดิบ (ไทย / อังกฤษ)")
      new_category = st.selectbox("หมวดหมู่วัตถุดิบ", categories)
    with col2:
      new_unit = st.text_input("หน่วยนับ (เช่น Kg., Pack, Bottle, Pcs.)")
      new_price = st.number_input(
          "ราคาตั้งต้น / ราคาล่าสุดต่อหน่วย (บาท)", min_value=0.0, step=0.1
      )
      new_stock = st.number_input("ยอดสต็อกเริ่มต้น", min_value=0.0, step=0.1)

    submit_button = st.form_submit_button(label="บันทึกเพิ่มสินค้า")

    if submit_button:
      if new_code and new_name:
        new_row = pd.DataFrame({
            "Product Code": [new_code],
            "Item Name": [new_name],
            "Category": [new_category],
            "Unit": [new_unit],
            "Stock Balance": [new_stock],
            "Last Price": [new_price],
        })
        st.session_state.company_inventories[selected_company] = pd.concat(
            [current_inv, new_row], ignore_index=True
        )
        st.success(f"เพิ่มวัตถุดิบ '{new_name}' สำเร็จเรียบร้อย!")
        st.rerun()
      else:
        st.error("กรุณากรอกรหัสสินค้าและชื่อสินค้าให้ครบถ้วน")

  st.subheader("รายการสินค้าทั้งหมดในบริษัทนี้")
  st.dataframe(
      st.session_state.company_inventories[selected_company],
      use_container_width=True,
  )

# ---------------------------------------------------------
# เมนูที่ 3: บันทึกรับเข้าสินค้า (Stock In)
# ---------------------------------------------------------
elif menu == "📥 บันทึกรับเข้าสินค้า (Stock In)":
  st.header(f"บันทึกรับเข้าวัตถุดิบ: {selected_company}")

  if len(current_inv) > 0:
    with st.form("stock_in_form"):
      st.subheader("📝 รายละเอียดการรับเข้าสินค้า")

      col1, col2 = st.columns(2)
      with col1:
        selected_item = st.selectbox(
            "เลือกวัตถุดิบที่มีในระบบ", current_inv["Item Name"].tolist()
        )
        purchase_date = st.date_input(
            "วันที่ซื้อ / รับเข้า", value=datetime.today()
        )
        supplier_name = st.text_input(
            "ร้านค้าที่ซื้อ (เช่น Big Green, Makro ฯลฯ)"
        )
      with col2:
        qty_in = st.number_input(
            "จำนวนที่รับเข้า", min_value=0.1, step=0.1, value=1.0
        )
        actual_price = st.number_input(
            "ราคาต่อหน่วยในวันนี้ (บาท)", min_value=0.0, step=0.1, value=10.0
        )
        vat_type = st.selectbox("ประเภทภาษี", ["Non Vat", "Vat 7%"])

      submit_in = st.form_submit_button(label="ยืนยันการรับเข้าสินค้า")

      if submit_in:
        if supplier_name:
          base_total = qty_in * actual_price
          if vat_type == "Vat 7%":
            final_total = base_total * 1.07
          else:
            final_total = base_total

          idx = current_inv[current_inv["Item Name"] == selected_item].index[0]

          old_stock = current_inv.loc[idx, "Stock Balance"]
          new_stock_balance = old_stock + qty_in

          st.session_state.company_inventories[selected_company].loc[
              idx, "Stock Balance"
          ] = new_stock_balance
          st.session_state.company_inventories[selected_company].loc[
              idx, "Last Price"
          ] = actual_price

          new_trans = pd.DataFrame({
              "Company": [selected_company],
              "Date": [str(purchase_date)],
              "Supplier": [supplier_name],
              "Item Name": [selected_item],
              "Quantity": [qty_in],
              "Price/Unit": [actual_price],
              "Vat Type": [vat_type],
              "Total Price": [final_total],
          })
          st.session_state.transactions = pd.concat(
              [st.session_state.transactions, new_trans], ignore_index=True
          )

          st.success(
              f"บันทึกรับเข้า '{selected_item}' จำนวน {qty_in} จากร้าน"
              f" '{supplier_name}' ({vat_type}) ยอดรวมสุทธิ"
              f" {final_total:,.2f} บาท สำเร็จ!"
          )
        else:
          st.error("กรุณาระบุชื่อร้านค้าที่ซื้อ")
  else:
    st.warning("ยังไม่มีรายการสินค้า กรุณาเพิ่มสินค้าในเมนูก่อนครับ")

# ---------------------------------------------------------
# เมนูที่ 4: ประวัติการรับสินค้า / รายงานสิ้นเดือน
# ---------------------------------------------------------
elif menu == "📜 ประวัติการรับสินค้า":
  st.header(f"รายงานการรับสินค้าและสรุปสิ้นเดือน: {selected_company}")
  trans_df = st.session_state.transactions

  if len(trans_df) > 0:
    comp_trans = trans_df[trans_df["Company"] == selected_company].copy()

    if len(comp_trans) > 0:
      comp_trans["Date_dt"] = pd.to_datetime(comp_trans["Date"])

      col1, col2 = st.columns(2)
      with col1:
        available_years = sorted(
            comp_trans["Date_dt"].dt.year.unique(), reverse=True
        )
        selected_year = st.selectbox("เลือกปี", available_years)

      with col2:
        available_months = sorted(
            comp_trans[comp_trans["Date_dt"].dt.year == selected_year][
                "Date_dt"
            ]
            .dt.month.unique()
        )
        selected_month = st.selectbox("เลือกเดือน", available_months)

      monthly_report = comp_trans[
          (comp_trans["Date_dt"].dt.year == selected_year)
          & (comp_trans["Date_dt"].dt.month == selected_month)
      ].drop(columns=["Date_dt"])

      st.subheader(
          f"รายงานประจำเดือน {selected_month}/{selected_year}"
          f" (ยอดรวม {monthly_report['Total Price'].sum():,.2f} บาท)"
      )
      st.dataframe(monthly_report, use_container_width=True)

      csv_data = monthly_report.to_csv(index=False).encode("utf-8-sig")
      st.download_button(
          label="📥 ดาวน์โหลดรายงานฉบับนี้ (CSV)",
          data=csv_data,
          file_name=(
              f"Stock_Report_{selected_company}_{selected_year}-{selected_month:02d}.csv"
          ),
          mime="text/css",
      )
    else:
      st.info(f"ยังไม่มีประวัติการรับสินค้าของบริษัท {selected_company}")
  else:
    st.info("ยังไม่มีประวัติการทำรายการรับเข้าสินค้าในระบบ")
