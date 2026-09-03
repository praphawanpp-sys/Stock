import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ตรวจสอบและตั้งค่า Session State เพิ่มเติมสำหรับการขยายระบบ
if 'suppliers_db' not in st.session_state:
    st.session_state['suppliers_db'] = pd.DataFrame([
        {"Supplier Code": "SUP-001", "Supplier Name": "Thai Dairy Co., Ltd.", "Contact": "คุณสมชาย", "Phone": "081-234-5678", "Email": "order@thaidairy.com", "Tax ID": "0105558000111", "Credit Days": 30, "Status": "Active"},
        {"Supplier Code": "SUP-002", "Supplier Name": "Bakery Supply Hub", "Contact": "คุณวิภา", "Phone": "089-876-5432", "Email": "sales@bakeryhub.com", "Tax ID": "0105559000222", "Credit Days": 15, "Status": "Active"}
    ])

if 'receiving_list' not in st.session_state:
    st.session_state['receiving_list'] = pd.DataFrame(columns=[
        "Receiving No", "PO Number", "Branch", "Supplier", "Receive Date", "Items Received", "Status"
    ])

if 'stock_balance' not in st.session_state:
    # Stock แยกตาม Branch และ SKU
    st.session_state['stock_balance'] = pd.DataFrame([
        {"Branch": "Daddy Deli (Head Office)", "SKU": "SKU-001", "Product Name": "แป้งเค้ก (Cake Flour)", "Balance Qty": 50.0, "Unit": "kg"},
        {"Branch": "Harvest Cafe (Branch 0001)", "SKU": "SKU-001", "Product Name": "แป้งเค้ก (Cake Flour)", "Balance Qty": 20.0, "Unit": "kg"},
        {"Branch": "Harvest Cafe (Branch 0001)", "SKU": "SKU-002", "Product Name": "นมสด (Fresh Milk)", "Balance Qty": 15.0, "Unit": "L"}
    ])

# เพิ่มเมนูนำทางเสริม
st.sidebar.markdown("---")
extended_menu = st.sidebar.radio("Advanced Modules", [
    "Dashboard Overview", 
    "Purchase Request (PR)", 
    "Purchase Order (PO)", 
    "Goods Receiving & Stock In", 
    "Supplier Management", 
    "Audit Logs & Security"
])

# ----------------------------------------------------
# MODULE: GOODS RECEIVING & STOCK INTEGRATION (Rule 14)
# ----------------------------------------------------
if extended_menu == "Goods Receiving & Stock In":
    st.title("📦 Goods Receiving & Stock In (Inventory Integration)")
    st.info("📌 กฎเหล็ก: PO จะไม่ตัด Stock ทันที Stock จะเพิ่มเฉพาะเมื่อมีการกด Receive (ตรวจรับสินค้าจริง) เท่านั้น")
    
    approved_pos = st.session_state['po_list'][st.session_state['po_list']['Status'].isin(["Approved", "Sent to Supplier", "Partially Received"])]
    
    if len(approved_pos) > 0:
        with st.form("receiving_form"):
            selected_po = st.selectbox("เลือก PO ที่ต้องการรับสินค้า", approved_pos['PO Number'].tolist())
            po_row = st.session_state['po_list'][st.session_state['po_list']['PO Number'] == selected_po].iloc[0]
            
            st.write(f"🏢 สาขา: {po_row['Branch']} | 🚚 Supplier: {po_row['Supplier']}")
            
            col1, col2 = st.columns(2)
            with col1:
                ordered_qty = st.number_input("จำนวนที่สั่งทั้งหมด (Ordered)", value=100.0, disabled=True)
                receive_qty = st.number_input("จำนวนที่รับจริงงวดนี้ (Received Qty)", min_value=0.0, value=70.0)
            with col2:
                receiver_name = st.text_input("ชื่อผู้ตรวจรับ", value="Staff Warehouse")
                note = st.text_area("หมายเหตุการรับสินค้า (เช่น กล่องบุบ 2 กล่อง)")
                
            submit_receive = st.form_submit_button("📥 บันทึกรับสินค้าและเข้า Stock")
            
            if submit_receive:
                rcv_num = f"RCV-{datetime.now().strftime('%m%d%H%M%S')}"
                outstanding = ordered_qty - receive_qty
                
                # อัปเดตสถานะ PO
                po_idx = st.session_state['po_list'][st.session_state['po_list']['PO Number'] == selected_po].index[0]
                if outstanding <= 0:
                    st.session_state['po_list'].loc[po_idx, 'Status'] = "Fully Received"
                    rcv_status = "Fully Received"
                else:
                    st.session_state['po_list'].loc[po_idx, 'Status'] = "Partially Received"
                    rcv_status = f"Partially Received (Outstanding: {outstanding})"
                
                # บันทึก Receiving Log
                new_rcv = pd.DataFrame([{
                    "Receiving No": rcv_num, "PO Number": selected_po, "Branch": po_row['Branch'],
                    "Supplier": po_row['Supplier'], "Receive Date": str(datetime.today().date()),
                    "Items Received": f"Qty: {receive_qty} (Status: {rcv_status})", "Status": rcv_status
                }])
                st.session_state['receiving_list'] = pd.concat([st.session_state['receiving_list'], new_rcv], ignore_index=True)
                
                # อัปเดต Stock Balance เฉพาะสาขานั้นๆ จริง (Rule 14)
                branch_filter = (st.session_state['stock_balance']['Branch'] == po_row['Branch']) & (st.session_state['stock_balance']['SKU'] == "SKU-001")
                if branch_filter.any():
                    st.session_state['stock_balance'].loc[branch_filter, 'Balance Qty'] += receive_qty
                else:
                    new_stock = pd.DataFrame([{"Branch": po_row['Branch'], "SKU": "SKU-001", "Product Name": "แป้งเค้ก (Cake Flour)", "Balance Qty": receive_qty, "Unit": "kg"}])
                    st.session_state['stock_balance'] = pd.concat([st.session_state['stock_balance'], new_stock], ignore_index=True)
                
                st.success(f"บันทึกรับสินค้าสำเร็จ ({rcv_num})! Stock ถูกปรับเพิ่มเฉพาะจำนวนที่รับจริงเรียบร้อยแล้ว")
                st.rerun()
    else:
        st.warning("ไม่มี PO ที่รอรับสินค้าในขณะนี้")
        
    st.markdown("### 📋 ประวัติการรับสินค้า (Receiving History)")
    if len(st.session_state['receiving_list']) > 0:
        st.dataframe(st.session_state['receiving_list'], use_container_width=True)
    else:
        st.info("ยังไม่มีประวัติการรับสินค้า")
        
    st.markdown("### 📊 ตรวจสอบ Stock คงเหลือแยกตามสาขา (Real-time Stock Balance)")
    st.dataframe(st.session_state['stock_balance'], use_container_width=True)

# ----------------------------------------------------
# MODULE: SUPPLIER MANAGEMENT
# ----------------------------------------------------
elif extended_menu == "Supplier Management":
    st.title("🏢 Supplier & Vendor Directory")
    
    with st.expander("➕ เพิ่ม Supplier ใหม่"):
        with st.form("add_sup_form"):
            s_code = st.text_input("Supplier Code", value="SUP-003")
            s_name = st.text_input("Supplier Name")
            s_contact = st.text_input("ชื่อผู้ติดต่อ")
            s_phone = st.text_input("เบอร์โทรศัพท์")
            s_credit = st.number_input("Credit Term (วัน)", min_value=0, value=30)
            
            if st.form_submit_button("Save Supplier"):
                new_s = pd.DataFrame([{"Supplier Code": s_code, "Supplier Name": s_name, "Contact": s_contact, "Phone": s_phone, "Email": "-", "Tax ID": "-", "Credit Days": s_credit, "Status": "Active"}])
                st.session_state['suppliers_db'] = pd.concat([st.session_state['suppliers_db'], new_s], ignore_index=True)
                st.success("บันทึกข้อมูล Supplier สำเร็จ")
                st.rerun()
                
    st.dataframe(st.session_state['suppliers_db'], use_container_width=True)

# ----------------------------------------------------
# MODULE: EXPORT & DOCUMENT PREVIEW (Rule 10 & 11)
# ----------------------------------------------------
elif extended_menu == "Purchase Order (PO)":
    # ส่วนเสริมในหน้า PO เดิม สำหรับพรีวิวและ Export Excel / PDF Mockup
    st.title("📄 Purchase Order Document & Export Center")
    
    if len(st.session_state['po_list']) > 0:
        selected_po_exp = st.selectbox("เลือก PO สำหรับพิมพ์ / Export เอกสาร", st.session_state['po_list']['PO Number'].tolist())
        po_row = st.session_state['po_list'][st.session_state['po_list']['PO Number'] == selected_po_exp].iloc[0]
        
        # Document Preview Template (Rule 11)
        st.markdown(f"""
        ---
        ### 🏢 Daddy Deli & Restaurant Group (Head Office)
        **ที่ตั้ง:** 99/9 ถ.สุขุมวิท กรุงเทพฯ | **Tax ID:** 0105555000999
        
        ---
        ## **PURCHASE ORDER (ใบสั่งซื้อสินค้า)**
        * **PO Number:** {po_row['PO Number']}
        * **Reference PR:** {po_row['PR Number']}
        * **Date:** {po_row['Date']}
        * **Branch:** {po_row['Branch']}
        * **Supplier:** {po_row['Supplier']}
        
        | No. | Product / Ingredient | SKU | Qty | Unit | Unit Price (THB) | Total (THB) |
        | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
        | 1 | แป้งเค้ก (Cake Flour) | SKU-001 | 20 | kg | 45.00 | 900.00 |
        | 2 | นมสด (Fresh Milk) | SKU-002 | 30 | L | 32.00 | 960.00 |
        
        * **Subtotal:** 1,860.00 THB
        * **VAT (7%):** 130.20 THB
        * **Grand Total:** **1,990.20 THB**
        
        ---
        *Prepared By:* {st.session_state.get('current_user', 'Staff')} | *Approved By:* Management Team
        ---
        """, unsafe_allow_html=True)
        
        # Export Actions (Rule 10)
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            if st.button("📊 Export Selected PO to Excel (.xlsx)"):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    pd.DataFrame([po_row]).to_excel(writer, index=False, sheet_name='PO_Detail')
                st.download_button(label="📥 ดาวน์โหลดไฟล์ Excel", data=output.getvalue(), file_name=f"{selected_po_exp}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col_ex2:
            if st.button("🖨️ Print / Save as PDF"):
                st.info("ระบบจัดเตรียมหน้าต่าง Print กำลังเปิดใช้งาน... (สามารถกด Ctrl+P เพื่อพิมพ์เอกสารนี้ผ่าน Browser ได้ทันที)")
    else:
		    st.info("ยังไม่มีข้อมูล PO ในระบบสำหรับทำเอกสาร")
