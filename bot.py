import asyncio
import pandas as pd
from telegram import Bot
from settings import (
    NUPL_THRESHOLDS, 
    MVRV_LTH_THRESHOLDS, 
    MVRV_STH_THRESHOLDS, 
    SOPR_STH_THRESHOLDS,
    NUPL_MESSAGES,
    MVRV_LTH_MESSAGES,
    MVRV_STH_MESSAGES,
    SOPR_STH_MESSAGES
)

async def send_message(token, chat_id, message):
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def get_status(value, thresholds):
    for status, (min_val, max_val) in thresholds.items():
        if min_val <= value < max_val:
            return status
    return 'high' if value >= max_val else 'low'

def format_metrics(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Extract specific metrics and format them
    latest_data = df.iloc[-1]
    previous_data = df.iloc[-2]
    
    date = latest_data['date']
    nupl = latest_data['NUPL']
    mvrv_lth = latest_data['MVRV_LTH']
    mvrv_sth = latest_data['MVRV_STH']
    sopr_sth = latest_data['SOPR_STH']
    realized_cap = latest_data['RealizedCap']
    
    # Determine current insights
    nupl_status = get_status(nupl, NUPL_THRESHOLDS)
    mvrv_lth_status = get_status(mvrv_lth, MVRV_LTH_THRESHOLDS)
    mvrv_sth_status = get_status(mvrv_sth, MVRV_STH_THRESHOLDS)
    sopr_sth_status = get_status(sopr_sth, SOPR_STH_THRESHOLDS)
    
    # Check for status changes
    alert_messages = []
    
    # Compare with previous values and add alerts for any changes
    prev_nupl_status = get_status(previous_data['NUPL'], NUPL_THRESHOLDS)
    prev_mvrv_lth_status = get_status(previous_data['MVRV_LTH'], MVRV_LTH_THRESHOLDS)
    prev_mvrv_sth_status = get_status(previous_data['MVRV_STH'], MVRV_STH_THRESHOLDS)
    prev_sopr_sth_status = get_status(previous_data['SOPR_STH'], SOPR_STH_THRESHOLDS)
    
    if nupl_status != prev_nupl_status:
        alert_messages.append(f"⚠️ NUPL status changed from {prev_nupl_status} to {nupl_status}")
    if mvrv_lth_status != prev_mvrv_lth_status:
        alert_messages.append(f"⚠️ LTH-MVRV status changed from {prev_mvrv_lth_status} to {mvrv_lth_status}")
    if mvrv_sth_status != prev_mvrv_sth_status:
        alert_messages.append(f"⚠️ STH-MVRV status changed from {prev_mvrv_sth_status} to {mvrv_sth_status}")
    if sopr_sth_status != prev_sopr_sth_status:
        alert_messages.append(f"⚠️ STH-SOPR status changed from {prev_sopr_sth_status} to {sopr_sth_status}")
    
    # Format the message with extra line breaks between metrics
    message = (
        f"📅 Date: {date}\n\n"
        f"🔹 NUPL: {nupl:.2f} ({nupl_status}) - {NUPL_MESSAGES[nupl_status]}\n\n"
        f"🔹 LTH-MVRV: {mvrv_lth:.2f} ({mvrv_lth_status}) - {MVRV_LTH_MESSAGES[mvrv_lth_status]}\n\n"
        f"🔹 STH-MVRV: {mvrv_sth:.2f} ({mvrv_sth_status}) - {MVRV_STH_MESSAGES[mvrv_sth_status]}\n\n"
        f"🔹 STH-SOPR: {sopr_sth:.2f} ({sopr_sth_status}) - {SOPR_STH_MESSAGES[sopr_sth_status]}\n\n"
        f"🔹 Realized Cap: ${realized_cap/1e9:,.2f}B\n\n"
    )
    
    if alert_messages:
        message += "ALERTS:\n" + "\n".join(alert_messages)
    
    return message

if __name__ == "__main__":
    token = "7551468775:AAElQwkgWIYoBK1oX-yyi2K9RZz6_zSVTiI"
    chat_id = "2123714800"
    file_path = 'checkonchain.csv'
    
    message = format_metrics(file_path)
    asyncio.run(send_message(token, chat_id, message))
