import numpy as np
import pandas as pd
import streamlit as st
from io import BytesIO

# -----------------------------------
# Fungsi Weighted Product
# -----------------------------------
def weighted_product(X, weights, criteria_type, alternatives, criteria):
    """
    Implementasi metode Weighted Product (WP)

    X             : numpy array, shape (n_alt, n_crit)
    weights       : list/array bobot kriteria (panjang = n_crit)
    criteria_type : list tipe kriteria, 'benefit' atau 'cost'
    alternatives  : list nama alternatif
    criteria      : list nama kriteria (tidak terlalu dipakai di WP, tapi disimpan bila perlu)
    """

    X = np.array(X, dtype=float)
    w = np.array(weights, dtype=float)

    # Normalisasi bobot agar jumlah = 1
    if not np.isclose(w.sum(), 1.0):
        w = w / w.sum()

    # Ubah bobot kriteria cost menjadi negatif (WP pakai pangkat negatif utk cost)
    w_wp = w.copy()
    for j, t in enumerate(criteria_type):
        if t.lower().strip() == "cost":
            w_wp[j] = -w_wp[j]

    # Hitung vektor S: Si = Π_j (x_ij ^ wj)
    S = np.prod(X ** w_wp, axis=1)

    # Hitung vektor V: Vi = Si / Σ Si
    S_total = S.sum()
    V = S / S_total

    # Susun hasil ke DataFrame
    df_result = pd.DataFrame({
        "Alternatif": alternatives,
        "Nilai_S": S,
        "Nilai_V": V
    })

    # Urutkan dari terbaik (V terbesar)
    df_result = df_result.sort_values(by="Nilai_V", ascending=False).reset_index(drop=True)

    return df_result


# -----------------------------------
# Aplikasi Streamlit
# -----------------------------------
st.set_page_config(
    page_title="SPK - Weighted Product",
    layout="centered"
)

st.title("🧮 Sistem Pendukung Keputusan")
st.subheader("Metode Weighted Product (WP)")

st.markdown(
    """
Aplikasi ini menggunakan metode **Weighted Product (WP)** untuk melakukan perangkingan alternatif.

**Langkah penggunaan:**
1. Siapkan file **Excel** dengan format:
   - Kolom pertama: nama/ID **Alternatif**
   - Kolom berikutnya: nilai-nilai **kriteria**
2. Upload file Excel.
3. Masukkan **bobot** dan **tipe kriteria** (benefit/cost) sesuai urutan kolom kriteria.
4. Klik tombol **Proses SPK** untuk melihat hasil perangkingan.
"""
)

# Upload file Excel
uploaded_file = st.file_uploader("Upload file Excel (.xlsx / .xls)", type=["xlsx", "xls"])

# Input bobot & tipe kriteria
st.markdown("### Parameter Kriteria")

weights_input = st.text_input(
    "Bobot kriteria (dipisah koma, urut sesuai kolom di Excel setelah 'Alternatif')",
    placeholder="Contoh: 0.28,0.22,0.11,0.22,0.17"
)

criteria_types_input = st.text_input(
    "Tipe kriteria (benefit / cost, dipisah koma)",
    placeholder="Contoh: benefit,benefit,cost,benefit,benefit"
)

proses = st.button("🔍 Proses SPK")

if proses:
    # Validasi input file
    if uploaded_file is None:
        st.error("Silakan upload file Excel terlebih dahulu.")
    elif not weights_input.strip() or not criteria_types_input.strip():
        st.error("Bobot dan tipe kriteria tidak boleh kosong.")
    else:
        # Baca Excel
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Gagal membaca file Excel: {e}")
            st.stop()

        # Minimal 2 kolom: Alternatif + 1 kriteria
        if df.shape[1] < 2:
            st.error("Format Excel tidak sesuai. Minimal harus ada kolom 'Alternatif' dan satu kolom kriteria.")
            st.stop()

        # Ambil nama alternatif & matriks kriteria
        alternatives = df.iloc[:, 0].astype(str).tolist()
        criteria = df.columns[1:].tolist()
        X = df.iloc[:, 1:].values

        n_crit = len(criteria)

        # Parsing bobot
        try:
            weights = [float(w) for w in weights_input.split(",") if w.strip() != ""]
        except ValueError:
            st.error("Format bobot tidak valid. Pastikan hanya berisi angka dipisah koma.")
            st.stop()

        # Parsing tipe kriteria
        criteria_type = [t.strip().lower() for t in criteria_types_input.split(",") if t.strip() != ""]

        # Validasi panjang
        if len(weights) != n_crit:
            st.error(f"Jumlah bobot ({len(weights)}) tidak sama dengan jumlah kriteria ({n_crit}).")
            st.stop()

        if len(criteria_type) != n_crit:
            st.error(f"Jumlah tipe kriteria ({len(criteria_type)}) tidak sama dengan jumlah kriteria ({n_crit}).")
            st.stop()

        # Tampilkan data awal
        st.markdown("### Data Alternatif & Kriteria (dari Excel)")
        st.dataframe(df, use_container_width=True)

        # Tampilkan info kriteria
        st.markdown("### Informasi Kriteria")
        info_kriteria = pd.DataFrame({
            "Kriteria": criteria,
            "Bobot": weights,
            "Tipe": criteria_type
        })
        st.table(info_kriteria)

        # Hitung Weighted Product
        hasil_wp = weighted_product(X, weights, criteria_type, alternatives, criteria)

        st.markdown("### Hasil Perhitungan & Perangkingan (Metode WP)")
        st.dataframe(hasil_wp, use_container_width=True)

        # Download hasil sebagai Excel

        buffer = BytesIO()

        # Tulis dataframe ke buffer Excel
        hasil_wp.to_excel(buffer, index=False, sheet_name="Hasil_WP")
        buffer.seek(0)


st.download_button(
    label="💾 Download Hasil dalam Excel",
    data=buffer,
    file_name="hasil_spk_wp.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)   


st.success("Perhitungan SPK dengan metode Weighted Product selesai.")
