def verify_certificate(certificate_hash: str):
    """
    Simulasi verifikasi sertifikat.
    Blockchain akan ditambahkan di tahap berikutnya.
    """

    # Contoh logika sederhana
    if certificate_hash.startswith("VALID"):
        return {
            "status": "VALID",
            "message": "Sertifikat terverifikasi"
        }
    else:
        return {
            "status": "TIDAK VALID",
            "message": "Sertifikat tidak ditemukan"
        }
