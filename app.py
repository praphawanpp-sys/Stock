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

# หน่วยนับที่เพิ่มตามที่คุณต้องการ
unit_options = [
    "Kg.",
    "Gram",
    "Pack",
    "Bottle",
    "Can",
    "Box",
    "Pcs.",
    "Bag",
    "Litres",
    "Tray",
    "Gallon",
    "Case",
    "Jar",
    "Cup",
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

# 1. เลือกบริษัท / สาขา ที่ Sidebar
selected_company = st.sidebar.selectbox(
    "🏢 กรุณาเลือกบริษัท / สาขา:", companies
)

st.sidebar.markdown("---")

# 2. เลือกเมนูการใช้งาน (เพิ่มเมนูนับสต็อกสิ้นเดือนแล้ว)
menu = st.selectbox(
    "📌 เลือกเมนูการใช้งาน",
    [
        "📊 หน้าแรก / สรุปภาพรวม",
        "📦 จัดการรายการสินค้า (Master)",
        "📥 บันทึกรับเข้าสินค้า (Stock In)",
        "📜 ประวัติการรับสินค้า",
        "📋 นับสต็อกตอนสิ้นเดือน (End of Month)",
    ],
)

st.markdown("---")

# ดึงข้อมูลของบริษัทที่ถูกเลือกปัจจุบัน
current_inv = st.session_state.company_inventories[selected_company]
trans_df = st.session_state.transactions

# ดึงรายชื่อ Supplier เก่าจากระบบ (ถ้ามี) มาทำ Dropdown
existing_suppliers = (
    trans_df["Supplier"].unique().tolist() if len(trans_df) > 0 else []
)

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
        f"ยังไม่มีข้อมูลสินค้าใน {selected_company}"
        " กรุณาเพิ่มสินค้าหรือนำเข้าจากไฟล์ Excel"
    )

# ---------------------------------------------------------
# เมนูที่ 2: จัดการรายการสินค้า (Product Master & Import Excel)
# ---------------------------------------------------------
elif menu == "📦 จัดการรายการสินค้า (Master)":
  st.header(f"จัดการรายการวัตถุดิบ: {selected_company}")

  # 📂 ส่วนนำเข้าข้อมูลจากไฟล์ Excel หรือ CSV
  with st.expander("📥 นำเข้าข้อมูลรายการสินค้าจากไฟล์ Excel / CSV"):
    uploaded_file = st.file_uploader(
        "เลือกไฟล์ Excel หรือ CSV", type=["xlsx", "csv"]
    )
    if uploaded_file is not None:
      try:
        if uploaded_file.name.endswith(".csv"):
          df_import = pd.read_csv(uploaded_file)
        else:
          df_import = pd.read_excel(uploaded_file)

        st.write("ตัวอย่างข้อมูลที่อ่านได้:")
        st.dataframe(df_import.head())

        if st.button("ยืนยันการนำเข้าข้อมูลเข้าสู่ระบบ"):
          required_cols = [
              "Item Name",
              "Category",
              "Unit",
              "Stock Balance",
              "Last Price",
          ]
          if all(col in df_import.columns for col in required_cols):
            if "Product Code" not in df_import.columns:
              df_import["Product Code"] = "AUTO-IMP"

            st.session_state.company_inventories[selected_company] = (
                pd.concat(
                    [
                        st.session_state.company_inventories[selected_company],
                        df_import[
                            [
                                "Product Code",
                                "Item Name",
                                "Category",
                                "Unit",
                                "Stock Balance",
                                "Last Price",
                            ]
                        ],
                    ],
                    ignore_index=True,
                )
                .drop_duplicates(subset=["Item Name"], keep="last")
            )
            st.success("นำเข้าข้อมูลสำเร็จ!")
            st.rerun()
          else:
            st.error(
                "ชื่อคอลัมน์ในไฟล์ไม่ถูกต้อง (ต้องมี Item Name, Category, Unit,"
                " Stock Balance, Last Price)"
            )
      except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")

  st.markdown("---")

  with st.form("add_product_form", clear_on_submit=True):
    st.subheader("➕ เพิ่มวัตถุดิบ / บันทึกรับเข้า")

    col1, col2 = st.columns(2)
    with col1:
      # ชื่อ Supplier แบบ Dropdown / พิมพ์ใหม่
      sup_mode = st.radio(
          "รูปแบบการเลือกชื่อ Supplier",
          ["เลือกจากประวัติเดิม", "พิมพ์ชื่อ Supplier ใหม่"],
          horizontal=True,
      )
      if sup_mode == "เลือกจากประวัติเดิม" and len(existing_suppliers) > 0:
        supplier_name = st.selectbox("1. ชื่อ Supplier", existing_suppliers)
      else:
        supplier_name = st.text_input(
            "1. ชื่อ Supplier ใหม่ (เช่น Makro, Big Green)"
        )

      purchase_date = st.date_input("2. วันที่รับเข้า", value=datetime.today())

      existing_items = (
          current_inv["Item Name"].tolist() if len(current_inv) > 0 else []
      )
      item_mode = st.radio(
          "รูปแบบชื่อวัตถุดิบ",
          ["เลือกจากที่มีอยู่เดิม", "พิมพ์ชื่อวัตถุดิบใหม่"],
          horizontal=True,
      )
      if item_mode == "เลือกจากที่มีอยู่เดิม" and len(existing_items) > 0:
        item_name = st.selectbox("3. ชื่อวัตถุดิบ", existing_items)
      else:
        item_name = st.text_input("3. ชื่อวัตถุดิบใหม่ (ไทย / อังกฤษ)")

      quantity = st.number_input(
          "4. จำนวนสินค้า", min_value=0.0, step=0.1, value=1.0
      )

    with col2:
      # หน่วยนับแบบ Dropdown ตามรายการที่คุณต้องการ
      unit = st.selectbox("5. หน่วยนับ", unit_options)

      price = st.number_input(
          "6. ราคาต่อหน่วย (บาท)", min_value=0.0, step=0.1, value=0.0
      )
      vat_type = st.selectbox("ประเภทภาษี (Vat)", ["Non Vat", "Vat 7%"])
      category = st.selectbox("7. หมวดหมู่วัตถุดิบ", categories)

    product_code = st.text_input(
        "รหัสสินค้า (Product Code) - ถ้ามี", value="AUTO-001"
    )

    submit_button = st.form_submit_button(label="บันทึกข้อมูล")

    if submit_button:
      if item_name and supplier_name:
        base_total = quantity * price
        final_total = base_total * 1.07 if vat_type == "Vat 7%" else base_total

        if len(current_inv) > 0 and item_name in current_inv["Item Name"].values:
          idx = current_inv[current_inv["Item Name"] == item_name].index[0]
          old_stock = current_inv.loc[idx, "Stock Balance"]
          st.session_state.company_inventories[selected_company].loc[
              idx, "Stock Balance"
          ] = (old_stock + quantity)
          st.session_state.company_inventories[selected_company].loc[
              idx, "Last Price"
          ] = price
          st.session_state.company_inventories[selected_company].loc[
              idx, "Unit"
          ] = unit
          st.session_state.company_inventories[selected_company].loc[
              idx, "Category"
          ] = category
        else:
          new_row = pd.DataFrame({
              "Product Code": [product_code],
              "Item Name": [item_name],
              "Category": [category],
              "Unit": [unit],
              "Stock Balance": [quantity],
              "Last Price": [price],
          })
          st.session_state.company_inventories[selected_company] = pd.concat(
              [current_inv, new_row], ignore_index=True
          )

        new_trans = pd.DataFrame({
            "Company": [selected_company],
            "Date": [str(purchase_date)],
            "Supplier": [supplier_name],
            "Item Name": [item_name],
            "Quantity": [quantity],
            "Price/Unit": [price],
            "Vat Type": [vat_type],
            "Total Price": [final_total],
        })
        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, new_trans], ignore_index=True
        )

        st.success(
            f"บันทึกรายการ '{item_name}' จาก '{supplier_name}' สำเร็จ!"
        )
        st.rerun()
      else:
        st.error("กรุณากรอกชื่อ Supplier และชื่อวัตถุดิบให้ครบถ้วน")

  st.subheader("รายการสินค้าคงเหลือปัจจุบันในบริษัทนี้")
  st.dataframe(
      st.session_state.company_inventories[selected_company],
      use_container_width=True,
  )

# ---------------------------------------------------------
# เมนูที่ 3: บันทึกรับเข้าสินค้า (Stock In) - ปรับช่องร้านค้าเป็น Dropdown
# ---------------------------------------------------------
elif menu == "📥 บันทึกรับเข้าสินค้า (Stock In)":
  st.header(f"บันทึกรับเข้าวัตถุดิบเพิ่มเติม: {selected_company}")

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

        # ทำช่องร้านค้าที่ซื้อให้เป็น Dropdown (เลือกจากประวัติ หรือพิมพ์เพิ่ม)
        sup_in_mode = st.radio(
            "เลือกวิธีระบุ Supplier",
            ["เลือกจากประวัติเดิม", "พิมพ์ชื่อร้านค้าใหม่"],
            horizontal=True,
        )
        if sup_in_mode == "เลือกจากประวัติเดิม" and len(existing_suppliers) > 0:
          supplier_name = st.selectbox(
              "ชื่อ Supplier (ร้านค้าที่ซื้อ)", existing_suppliers
          )
        else:
          supplier_name = st.text_input("ชื่อ Supplier ใหม่ (ร้านค้าที่ซื้อ)")

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
          final_total = base_total * 1.07 if vat_type == "Vat 7%" else base_total

          idx = current_inv[current_inv["Item Name"] == selected_item].index[0]
          old_stock = current_inv.loc[idx, "Stock Balance"]
          st.session_state.company_inventories[selected_company].loc[
              idx, "Stock Balance"
          ] = (old_stock + qty_in)
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
              f" '{supplier_name}' สำเร็จ!"
          )
          st.rerun()
        else:
          st.error("กรุณาระบุชื่อ Supplier")
  else:
    st.warning("ยังไม่มีรายการสินค้า กรุณาเพิ่มสินค้าก่อนครับ")

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
          mime="text/csv",
      )
    else:
      st.info(f"ยังไม่มีประวัติการรับสินค้าของบริษัท {selected_company}")
  else:
    st.info("ยังไม่มีประวัติการทำรายการรับเข้าสินค้าในระบบ")

# ---------------------------------------------------------
# เมนูที่ 5: นับสต็อกตอนสิ้นเดือน (End of Month Stock Count)
# ---------------------------------------------------------
elif menu == "📋 นับสต็อกตอนสิ้นเดือน (End of Month)":
  st.header(f"นับสต็อกคงเหลือหน้างานประจำสิ้นเดือน: {selected_company}")

  if len(current_inv) > 0:
    st.write(
        "กรุณากรอก **'ยอดนับจริง (Actual Count)'** ลงในตารางด้านล่างนี้"
        " เพื่อปรับปรุงยอดสต็อกให้ตรงกับหน้างานจริง"
    )

    # สร้างตารางจำลองสำหรับการแก้ไขยอดนับจริง
    count_df = current_inv[["Item Name", "Category", "Unit", "Stock Balance"]].copy()
    count_df.rename(
        columns={"Stock Balance": "System Balance (ยอดในระบบ)"}, inplace=True
    )
    count_df["Actual Count (ยอดนับจริง)"] = count_df[
        "System Balance (ยอดในระบบ)"
    ]

    # ใช้ data_editor ให้ผู้ใช้นัปและแก้ไขยอดจริงได้
    edited_df = st.data_editor(
        count_df,
        column_config={
            "Actual Count (ยอดนับจริง)": st.column_config.NumberColumn(
                "Actual Count (ยอดนับจริง)", min_value=0.0, step=0.1, required=True
            )
        },
        disabled=["Item Name", "Category", "Unit", "System Balance (ยอดในระบบ)"],
        use_container_width=True,
    )

    if st.button("💾 บันทึกและปรับปรุงยอดสต็อกสิ้นเดือน"):
      for idx, row in edited_df.iterrows():
        item_name = row["Item Name"]
        actual_val = row["Actual Count (ยอดนับจริง)"]
        # อัปเดตสต็อกจริงลงในระบบหลัก
        orig_idx = current_inv[current_inv["Item Name"] == item_name].index[0]
        st.session_state.company_inventories[selected_company].loc[
            orig_idx, "Stock Balance"
        ] = actual_val

      st.success("บันทึกยอดนับสต็อกสิ้นเดือนและปรับปรุงยอดคงเหลือเรียบร้อยแล้ว!")
      st.rerun()
  else:
    st.info(
        f"ยังไม่มีรายการสินค้าใน {selected_company} กรุณาเพิ่มสินค้าก่อนนับสต็อก"
    )
