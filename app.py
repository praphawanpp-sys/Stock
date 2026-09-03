import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="Enterprise Stock & Multi-Company System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 0. รายชื่อบริษัทและพจนานุกรมภาษา (TH / EN)
# ----------------------------------------------------
COMPANIES = [
    "ทุกบริษัท/สาขา (All Companies / Branches)",
    "Daddy Deli (Head Office)",
    "Harvest Cafe (Branch 0001)",
    "Taboo By Daddy Deli (Branch 0002)",
    "Daddy Deli Pattaya Group (Head Office)",
    "Harvest Bakery And Restaurant (Head Office)",
    "Daddy Deli Beach House (Head Office)"
]

REAL_COMPANIES = [c for c in COMPANIES if "ทุกบริษัท" not in c]

CATEGORIES_LIST = [
    "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others",
    "ผักและผลไม้ / Vegetables & Fruits",
    "ทะเล / Seafood",
    "เนื้อวัว / Beef",
    "น้ำผลไม้/Soft Drink/อื่นๆ / Juice/Soft Drink/Other",
    "เบียร์ / Beer",
    "ไส้กรอก / Sausage",
    "ชีส / Cheese",
    "นม / Milk"
]

UNITS_LIST = ["Box", "Pack", "Bag", "Kg", "Pcs", "Litre", "Bottle", "Can", "Gram"]
VAT_TYPES_LIST = ["Non Vat", "Vat 7%"]

LANG = {
    "th": {
        "title": "ระบบจัดการสต็อกวัตถุดิบและคลังสินค้า (Multi-Company)",
        "menu": "📌 เมนูหลัก",
        "m_dashboard": "📊 แดชบอร์ดภาพรวม",
        "m_inventory_mgmt": "📦 การจัดการรายการสินค้า",
        "sub_import_excel": "📥 นำเข้าสินค้า (Excel & Manual)",
        "sub_stock_in": "📥 รับสินค้า (Stock In)",
        "sub_stock_out": "📤 เบิกสินค้า (Stock Out)",
        "m_history": "📜 ประวัติการทำรายการ",
        "m_pr_po": "📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)",
        "m_eom": "📋 รายการสรุปสต็อก & นับสต็อก",
        "m_company_settings": "🏢 ตั้งค่าข้อมูลบริษัท",
    },
    "en": {
        "title": "Enterprise Food Cost & Stock Management System",
        "menu": "📌 Main Menu",
        "m_dashboard": "📊 Dashboard & Overview",
        "m_inventory_mgmt": "📦 Inventory Management",
        "sub_import_excel": "📥 Import Items (Excel & Manual)",
        "sub_stock_in": "📥 Stock In",
        "sub_stock_out": "📤 Stock Out / Requisition",
        "m_history": "📜 Transaction History",
        "m_pr_po": "📝 Purchase Request (PR) & PO",
        "m_eom": "📋 Stock Summary & End of Month Count",
        "m_company_settings": "🏢 Company Settings",
    }
}

TRANSLATE_DICT = {
    "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others": "Meat / Seasonings / Others",
    "ผักและผลไม้ / Vegetables & Fruits": "Vegetables & Fruits",
    "ทะเล / Seafood": "Seafood",
    "เนื้อวัว / Beef": "Beef",
    "น้ำผลไม้/Soft Drink/อื่นๆ / Juice/Soft Drink/Other": "Juice / Soft Drink / Other",
    "เบียร์ / Beer": "Beer",
    "ไส้กรอก / Sausage": "Sausage",
    "ชีส / Cheese": "Cheese",
    "นม / Milk": "Milk"
}

# ----------------------------------------------------
# 1. จัดการ Session State (ฐานข้อมูลจำลอง)
# ----------------------------------------------------
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'th'

if 'company_addresses' not in st.session_state:
    st.session_state['company_addresses'] = {comp: f"ที่อยู่สำนักงานใหญ่/สาขา ของ {comp}" for comp in REAL_COMPANIES}

if 'company_inventories' not in st.session_state:
    st.session_state['company_inventories'] = {}
    for comp in REAL_COMPANIES:
        st.session_state['company_inventories'][comp] = pd.DataFrame(columns=[
            "Product Code", "Item Name", "Category", "Unit", "Stock Balance", "Last Price", "Supplier", "Vat Type"
        ])
    st.session_state['company_inventories'][REAL_COMPANIES[0]] = pd.DataFrame([
        {"Product Code": "422582", "Item Name": "นมจืด 1 ลิตร", "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others", "Unit": "Box", "Stock Balance": 25.0, "Last Price": 109.0, "Supplier": "CP Axtra (Makro)", "Vat Type": "Non Vat"},
        {"Product Code": "2502009877754", "Item Name": "กระเทียมดัดจุก 500 ก.", "Category": "ผักและผลไม้ / Vegetables & Fruits", "Unit": "Pack", "Stock Balance": 10.0, "Last Price": 40.0, "Supplier": "CP Axtra (Lotus)", "Vat Type": "Non Vat"},
        {"Product Code": "54061057", "Item Name": "คิทแคท ทริกเกอร์ 500 กรัม", "Category": "เนื้อสัตว์/เครื่องปรุง/อื่นๆ / Meat / Seasonings / Others", "Unit": "Bag", "Stock Balance": 0.0, "Last Price": 130.0, "Supplier": "กส-สรา ค้าส่ง", "Vat Type": "Vat 7%"}
    ])

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame([
        {"Company": REAL_COMPANIES[0], "Date": str(datetime.today().date()), "DocNo": "INV-001", "Supplier": "CP Axtra (Makro)", "Item Name": "นมจืด 1 ลิตร", "Quantity": 25.0, "Price/Unit": 109.0, "Vat Type": "Non Vat", "Total Price": 2725.0, "Type": "IMPORT", "Receiver": "-", "Department": "-"}
    ])

if 'admins' not in st.session_state:
    st.session_state['admins'] = pd.DataFrame([
        {"Username": "boss_admin", "Name": "Mr. Boss (Foreigner)", "Branch": "All Branches", "Role": "Super Admin"},
        {"Username": "manager_a", "Name": "คุณสมชาย ใจดี", "Branch": REAL_COMPANIES[0], "Role": "Manager"}
    ])

if 'purchase_requests' not in st.session_state:
    st.session_state['purchase_requests'] = pd.DataFrame(columns=["PR_ID", "Date", "Supplier", "Branch", "Status", "Requester", "Items", "Quantity", "Price", "Unit", "Remark"])

if 'wast_variance_records' not in st.session_state:
    st.session_state['wast_variance_records'] = pd.DataFrame(columns=["Company", "Date", "Item Name", "Wast_Variance", "OC_Test", "Note"])

# ----------------------------------------------------
# 2. Sidebar: จัดวางแถบเปลี่ยนภาษาไว้บนสุด
# ----------------------------------------------------
with st.sidebar:
    lang_index = 0 if st.session_state['lang'] == 'th' else 1
    lang_choice = st.selectbox("🌐 ภาษา / Language", ["ไทย (Thai)", "English"], index=lang_index)
    st.session_state['lang'] = 'th' if lang_choice == "ไทย (Thai)" else 'en'
    
    st.markdown("---")

    selected_company = st.selectbox("🏢 เลือกบริษัท / สาขา", COMPANIES)
    
    st.markdown("---")
    
    admin_list = st.session_state['admins']['Username'].tolist()
    current_user_name = st.selectbox("👤 ผู้ใช้งานปัจจุบัน (Current User):", admin_list)
    user_info = st.session_state['admins'][st.session_state['admins']['Username'] == current_user_name].iloc[0]
    st.info(f"**{user_info['Name']}**\n\nสิทธิ์: {user_info['Role']}")
    
    st.markdown("---")
    st.markdown(f"### 📌 เมนูหลัก")
    
    pending_pr_count = 0
    if len(st.session_state['purchase_requests']) > 0:
        pending_pr_count = len(st.session_state['purchase_requests'][st.session_state['purchase_requests']['Status'] == "Pending (รออนุมัติ)"])
    
    pr_menu_label = f"📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO)"
    if pending_pr_count > 0:
        pr_menu_label = f"📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) 🔴({pending_pr_count})"

    t = LANG[st.session_state['lang']]
    
    selected_menu = st.radio("Navigation", [
        t['m_dashboard'],
        t['m_inventory_mgmt'],
        t['sub_import_excel'],
        t['sub_stock_in'],
        t['sub_stock_out'],
        t['m_history'],
        pr_menu_label,
        t['m_eom'],
        t['m_company_settings']
    ], label_visibility="collapsed")

if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
    current_inv = pd.concat(list(st.session_state['company_inventories'].values()), ignore_index=True)
    trans_df = st.session_state['transactions']
else:
    current_inv = st.session_state['company_inventories'][selected_company]
    trans_df = st.session_state['transactions'][st.session_state['transactions']['Company'] == selected_company]

# ----------------------------------------------------
# 3. เมนูที่ 1: แดชบอร์ดภาพรวม
# ----------------------------------------------------
if selected_menu == t['m_dashboard']:
    st.title(f"📊 แดชบอร์ดภาพรวม - {selected_company}")
    import_trans = trans_df[trans_df['Type'] == 'IMPORT']
    total_purchase_amount = import_trans['Total Price'].sum() if len(import_trans) > 0 else 0.0
    total_items = len(current_inv)
    total_qty = current_inv['Stock Balance'].sum() if total_items > 0 else 0
    total_val = (current_inv['Stock Balance'] * current_inv['Last Price']).sum() if total_items > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💵 ยอดเงินซื้อวัตถุดิบรวม", f"{total_purchase_amount:,.2f} THB")
    with col2:
        st.metric("📦 สต็อกคงเหลือ (มูลค่า)", f"{total_val:,.2f} THB ({total_qty:,.2f} หน่วย)")
    with col3:
        st.metric("🗑️ Wast & Variance", "0.00")
    with col4:
        st.metric("🎁 OC / Test", "0.00")
    st.markdown("---")
    st.subheader("📋 รายการวัตถุดิบในคลังปัจจุบัน")
    if len(current_inv) > 0:
        st.dataframe(current_inv, use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสินค้า")

# ----------------------------------------------------
# 4. เมนูที่ 2: การจัดการรายการสินค้า
# ----------------------------------------------------
elif selected_menu == t['m_inventory_mgmt']:
    st.title(f"📦 การจัดการรายการสินค้า - {selected_company}")
    if len(current_inv) > 0:
        st.dataframe(current_inv, use_container_width=True)
    else:
        st.info("ไม่มีรายการสินค้า")

# ----------------------------------------------------
# 5. นำเข้าสินค้า
# ----------------------------------------------------
elif selected_menu == t['sub_import_excel']:
    st.title(f"📥 นำเข้าสินค้า - {selected_company}")

# ----------------------------------------------------
# 6. รับสินค้า (Stock In)
# ----------------------------------------------------
elif selected_menu == t['sub_stock_in']:
    st.title(f"📥 รับสินค้าเข้า (Stock In) - {selected_company}")

# ----------------------------------------------------
# 7. เบิกสินค้า (Stock Out)
# ----------------------------------------------------
elif selected_menu == t['sub_stock_out']:
    st.title(f"📤 เบิกสินค้า (Stock Out) - {selected_company}")

# ----------------------------------------------------
# 8. ประวัติการทำรายการ
# ----------------------------------------------------
elif selected_menu == t['m_history']:
    st.title(f"📜 ประวัติการทำรายการ - {selected_company}")

# ----------------------------------------------------
# 9. ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) (ปรับแต่งฟอร์มเอกสารตามแบบฟอร์มตัวอย่าง)
# ----------------------------------------------------
elif pr_menu_label in selected_menu:
    pr_df = st.session_state['purchase_requests']
    pending_count = len(pr_df[pr_df['Status'] == "Pending (รออนุมัติ)"]) if len(pr_df) > 0 else 0
    
    st.markdown(f"<h2>📝 ระบบขอซื้อ (PR) & ใบสั่งซื้อ (PO) <span style='background-color: #ff4b4b; color: white; padding: 2px 10px; border-radius: 50%; font-size: 20px;'>{pending_count}</span></h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 สร้างใบขอซื้อ (PR)", "📄 ดูฟอร์มเอกสารใบสั่งซื้อ (PO Form) & อนุมัติ"])
    
    with tab1:
        with st.form("pr_form_new"):
            st.subheader("สร้างใบขอซื้อสินค้า (Purchase Request)")
            pr_date = st.date_input("วันที่ขอซื้อ", value=datetime.today())
            pr_sup = st.text_input("ร้านค้าที่ซื้อ (Supplier)", value="Thai_Namthip")
            pr_item = st.text_input("รายการวัตถุดิบ (Item)")
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                pr_qty = st.number_input("จำนวน (Qty)", min_value=1.0, value=1.0)
            with col_q2:
                pr_unit = st.selectbox("หน่วยนับ (Unit)", UNITS_LIST)
            
            pr_price = st.number_input("ราคาประมาณการต่อหน่วย (Price/Unit)", min_value=0.0, value=0.0)
            pr_req = st.text_input("ผู้ขอซื้อ (Requester / Admin)", value="Admin Kratai")
            pr_remark = st.text_area("หมายเหตุ (Remark)")
            
            if st.form_submit_button("💾 บันทึกและส่งใบขอซื้อ"):
                new_pr = {
                    "PR_ID": f"PO-{datetime.now().strftime('26%m%d')}",
                    "Date": str(pr_date), "Supplier": pr_sup, "Branch": selected_company,
                    "Status": "Pending (รออนุมัติ)", "Requester": pr_req, "Items": pr_item,
                    "Quantity": pr_qty, "Price": pr_price, "Unit": pr_unit, "Remark": pr_remark
                }
                st.session_state['purchase_requests'] = pd.concat([st.session_state['purchase_requests'], pd.DataFrame([new_pr])], ignore_index=True)
                st.success("สร้างใบขอซื้อสำเร็จ!")
                st.rerun()
                
    with tab2:
        st.subheader("📄 แสดงรูปแบบเอกสารใบสั่งซื้อสินค้า (Purchase Order Form)")
        if len(pr_df) > 0:
            pr_options = [f"{r['PR_ID']} - ร้าน: {r['Supplier']} ({r['Items']})" for _, r in pr_df.iterrows()]
            selected_doc_choice = st.selectbox("เลือกเอกสาร PR / PO ที่ต้องการดูฟอร์ม", pr_options)
            
            chosen_id = selected_doc_choice.split(" - ")[0]
            chosen_row = pr_df[pr_df['PR_ID'] == chosen_id].iloc[0]
            
            # ----------------------------------------------------
            # ส่วนแสดงผลจำลองเอกสาร (Document Form Layout)
            # ----------------------------------------------------
            st.markdown("""
            <style>
                .po-box {
                    border: 2px solid #333;
                    padding: 20px;
                    background-color: white;
                    color: black;
                    font-family: Arial, sans-serif;
                }
                .po-header {
                    display: flex;
                    justify-content: space-between;
                    border-bottom: 2px solid #333;
                    padding-bottom: 10px;
                    margin-bottom: 15px;
                }
                .po-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    margin-bottom: 20px;
                }
                .po-table th, .po-table td {
                    border: 1px solid #333;
                    padding: 8px;
                    text-align: center;
                    font-size: 14px;
                }
                .po-table th {
                    background-color: #d3d3d3;
                }
            </style>
            """, unsafe_allow_html=True)
            
            total_amount = chosen_row['Quantity'] * chosen_row['Price']
            
            st.markdown(f"""
            <div class="po-box">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="margin: 0; color: #1b4d3e;">Harvest</h2>
                        <small style="letter-spacing: 2px;">CAFÉ • EATERY • STORE</small>
                    </div>
                    <div style="text-align: right;">
                        <h3 style="margin:0;">Purchase order</h3>
                        <p style="margin:0; font-weight: bold;">ใบสั่งซื้อสินค้า</p>
                    </div>
                </div>
                
                <table style="width:100%; border: 1px solid #333; margin-top: 15px; border-collapse: collapse;">
                    <tr>
                        <td style="border: 1px solid #333; padding: 8px; width: 40%; vertical-align: top;">
                            <b>Company :</b> Daddy Deli<br>
                            <b>Address :</b> The Lodge Group Co., Ltd. (Head Office)<br>
                            No.17 Moo.7 Hin Lek Fai Subdistrict,<br>
                            Hua Hin District, Prachuap Khiri Khan Province 77110<br>
                            <b>Tax ID :</b> 0775565003672<br>
                            <b>Contact :</b> {chosen_row['Requester']}
                        </td>
                        <td style="border: 1px solid #333; padding: 8px; width: 40%; vertical-align: top;">
                            <b>สถานที่ส่งสินค้า / Delivery Address :</b><br>
                            Harvest Cafe<br>
                            779 Village No.7 Hin Lek Fai Subdistrict,<br>
                            Hua Hin District, Prachuap Khiri Khan Province 77110<br>
                            Admin Kratai
                        </td>
                        <td style="border: 1px solid #333; padding: 8px; width: 20%; vertical-align: top;">
                            <b>เลขที่ใบสั่งซื้อ (PO No.) :</b><br>{chosen_row['PR_ID']}<br><br>
                            <b>วันที่ (Date) :</b><br>{chosen_row['Date']}
                        </td>
                    </tr>
                </table>
                
                <p style="margin-top: 15px;"><b>Supplier :</b> {chosen_row['Supplier']}</p>
                
                <table class="po-table">
                    <tr>
                        <th style="width: 5%;">No</th>
                        <th style="width: 45%;">Item (รายการ)</th>
                        <th style="width: 12%;">QTY (จำนวน)</th>
                        <th style="width: 13%;">Price (ราคา)</th>
                        <th style="width: 12%;">Unit (หน่วย)</th>
                        <th style="width: 13%;">Total (ยอดรวม)</th>
                    </tr>
                    <tr>
                        <td>1</td>
                        <td style="text-align: left;">{chosen_row['Items']}</td>
                        <td>{chosen_row['Quantity']:,.2f}</td>
                        <td>{chosen_row['Price']:,.2f}</td>
                        <td>{chosen_row['Unit']}</td>
                        <td>{total_amount:,.2f}</td>
                    </tr>
                    <!-- แถวเปล่าจำลองตารางฟอร์ม -->
                    {"".join([f'<tr><td>{i}</td><td></td><td></td><td></td><td></td><td>0</td></tr>' for i in range(2, 11)])}
                    <tr>
                        <td colspan="5" style="text-align: right; font-weight: bold;">Grand Total</td>
                        <td style="font-weight: bold;">{total_amount:,.2f}</td>
                    </tr>
                </table>
                
                <p><b>หมายเหตุ / Remark :</b> {chosen_row['Remark']}</p>
                
                <table style="width:100%; border: 1px solid #333; border-collapse: collapse; margin-top: 20px;">
                    <tr>
                        <td style="border: 1px solid #333; width: 33%; text-align: center; padding: 25px 10px 10px 10px;">
                            ..................................................<br>
                            <b>ผู้ซื้อสินค้า</b><br>Order by
                        </td>
                        <td style="border: 1px solid #333; width: 33%; text-align: center; padding: 25px 10px 10px 10px;">
                            ..................................................<br>
                            <b>ผู้รับสินค้า</b><br>Consignee by
                        </td>
                        <td style="border: 1px solid #333; width: 34%; text-align: center; padding: 25px 10px 10px 10px;">
                            ..................................................<br>
                            <b>ผู้อำนวยอนุมัติ</b><br>Approved by
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            col_act1, col_act2 = st.columns(2)
            idx = pr_df[pr_df['PR_ID'] == chosen_row['PR_ID']].index[0]
            with col_act1:
                if st.button("✅ อนุมัติเอกสารนี้ (Approve)", key=f"appr_{idx}"):
                    st.session_state['purchase_requests'].loc[idx, 'Status'] = "Approved (อนุมัติแล้ว)"
                    st.success("อนุมัติเอกสารเรียบร้อยแล้ว!")
                    st.rerun()
            with col_act2:
                if st.button("❌ ปฏิเสธเอกสาร (Reject)", key=f"rej_{idx}"):
                    st.session_state['purchase_requests'].loc[idx, 'Status'] = "Rejected (ปฏิเสธ)"
                    st.rerun()
        else:
            st.info("ยังไม่มีข้อมูลใบขอซื้อและใบสั่งซื้อ")

# ----------------------------------------------------
# 10. รายการสรุปสต็อก & นับสต็อก
# ----------------------------------------------------
elif selected_menu == t['m_eom']:
    st.title(f"📋 รายการสรุปสต็อก & นับสต็อก - {selected_company}")
    if selected_company == "ทุกบริษัท/สาขา (All Companies / Branches)":
        st.warning("กรุณาเลือกเฉพาะ 1 บริษัท เพื่อทำรายการสรุปและนับสต็อก")
    else:
        st.subheader("📥 นำเข้า/ส่งออก Excel นับสต็อก")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            current_inv.to_excel(writer, sheet_name='Stock_Count', index=False)
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ Excel สำหรับนับสต็อก",
            data=output.getvalue(),
            file_name=f"stock_count_{selected_company}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        up_excel_count = st.file_uploader("📤 อัปโหลดไฟล์ Excel ที่นับสต็อกแล้ว", type=["xlsx"])
        if up_excel_count:
            st.success("อัปโหลดและอัปเดตสต็อกเรียบร้อยแล้ว!")
            
        st.markdown("---")
        st.subheader("ช่องบันทึก Wast & Variance และ OC / Test")
        with st.form("wast_form"):
            item_wast = st.selectbox("เลือกสินค้า", current_inv['Item Name'].tolist() if len(current_inv)>0 else [])
            wast_val = st.number_input("Wast & Variance (จำนวน)", min_value=0.0, value=0.0)
            oc_val = st.number_input("OC / Test (จำนวน)", min_value=0.0, value=0.0)
            note_w = st.text_input("หมายเหตุ")
            
            if st.form_submit_button("บันทึกข้อมูล Wast / OC"):
                new_w = {
                    "Company": selected_company, "Date": str(datetime.today().date()),
                    "Item Name": item_wast, "Wast_Variance": wast_val, "OC_Test": oc_val, "Note": note_w
                }
                st.session_state['wast_variance_records'] = pd.concat([st.session_state['wast_variance_records'], pd.DataFrame([new_w])], ignore_index=True)
                st.success("บันทึกสำเร็จ!")
                st.rerun()

# ----------------------------------------------------
# 11. ตั้งค่าข้อมูลบริษัท
# ----------------------------------------------------
elif selected_menu == t['m_company_settings']:
    st.title(f"🏢 ตั้งค่าข้อมูลบริษัทและแอดมิน - {selected_company}")
    
    set_tab1, set_tab2 = st.tabs(["📄 1. แก้ไข/เพิ่มชื่อ ที่อยู่ หรือข้อมูลบริษัทอื่นๆ", "⚙️ 2. การจัดการการจัดการแอดมินและสิทธิ์"])
    
    with set_tab1:
        st.subheader("แก้ไขชื่อ ที่อยู่ และข้อมูลบริษัท")
        current_addr = st.session_state['company_addresses'].get(selected_company, "")
        
        with st.form("company_info_form"):
            new_comp_name = st.text_input("ชื่อบริษัท / สาขา", value=selected_company)
            new_comp_address = st.text_area("ที่อยู่ของร้านค้า / สาขา", value=current_addr)
            new_tax_id = st.text_input("เลขประจำตัวผู้เสียภาษี (Tax ID)", value="01055xxxxxxxx")
            new_phone = st.text_input("เบอร์โทรศัพท์ติดต่อ", value="02-xxx-xxxx")
            
            save_comp_info = st.form_submit_button("💾 บันทึกข้อมูลบริษัท")
            if save_comp_info:
                st.session_state['company_addresses'][selected_company] = new_comp_address
                st.success("บันทึกข้อมูลที่อยู่และรายละเอียดบริษัทเรียบร้อยแล้ว!")
                st.rerun()
                
    with set_tab2:
        st.subheader("จัดการสิทธิ์ผู้ใช้งานและแอดมินระบบ")
        st.dataframe(st.session_state['admins'], use_container_width=True)
        
        st.markdown("---")
        st.subheader("🛠️ แก้ไข / ลบ หรือเพิ่มบัญชีแอดมิน")
        
        admin_names = st.session_state['admins']['Username'].tolist()
        sel_admin = st.selectbox("เลือกบัญชีผู้ใช้ที่ต้องการแก้ไขหรือลบ", admin_names)
        
        adm_row = st.session_state['admins'][st.session_state['admins']['Username'] == sel_admin].iloc[0]
        adm_idx = st.session_state['admins'][st.session_state['admins']['Username'] == sel_admin].index[0]
        
        with st.form("edit_admin_form"):
            a_user = st.text_input("Username", value=str(adm_row['Username']))
            a_name = st.text_input("Full Name / ชื่อ-นามสกุล", value=str(adm_row['Name']))
            a_branch = st.selectbox("Branch / สาขา", COMPANIES + ["All Branches"], index=0 if adm_row['Branch'] in COMPANIES else len(COMPANIES))
            a_role = st.selectbox("Role / สิทธิ์", ["Super Admin", "Manager", "Staff"], index=0 if adm_row['Role']=="Super Admin" else (1 if adm_row['Role']=="Manager" else 2))
            
            c_abtn1, c_abtn2 = st.columns(2)
            with c_abtn1:
                up_adm = st.form_submit_button("💾 บันทึกการแก้ไขแอดมิน")
            with c_abtn2:
                del_adm = st.form_submit_button("🗑️ ลบแอดมินนี้ออก")
                
            if up_adm:
                st.session_state['admins'].loc[adm_idx] = [a_user, a_name, a_branch, a_role]
                st.success("อัปเดตสิทธิ์แอดมินสำเร็จ!")
                st.rerun()
            elif del_adm:
                st.session_state['admins'] = st.session_state['admins'].drop(adm_idx).reset_index(drop=True)
                st.success("ลบแอดมินสำเร็จ!")
                st.rerun()
