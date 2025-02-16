import os
import requests
import base64
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

OFFICE_ID = os.environ["MFW_EXPENSE_OFFICE_ID"]
headers = {
    "Authorization": f"Bearer {os.environ["MFW_EXPENSE_KEY"]}",
    "Content-Type": "application/json",
}

@tool
def upload_receipt_image(image_path: str, image_name: str) -> dict:
    """クラウド経費に領収書画像をアップロードする関数

    Args:
        image_path (str): アップロードする画像ファイルのパス
        image_name (str): アップロード時に使用するファイル名

    Returns:
        dict: アップロード結果のJSONレスポンス

    Raises:
        requests.exceptions.RequestException: API通信時のエラー
        IOError: ファイル読み込み時のエラー
    """
    try:    
        with open(image_path, 'rb') as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        url = f"https://expense.moneyforward.com/api/external/v1/offices/{OFFICE_ID}/me/upload_receipt" 
        
        payload = {
            "office_id": OFFICE_ID,
            "content": base64_image,
            "content_type": "image/jpeg",
            "filename": image_name,
            "process_type": "2"            
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
        
    except (IOError, requests.exceptions.RequestException) as e:
        raise Exception(f"領収書のアップロードに失敗しました: {str(e)}")

@tool
def get_expense_reports() -> dict:
    """経費レポートの一覧を取得する

    Returns:
        dict: 経費レポートの一覧
    
    Raises:
        requests.exceptions.RequestException: API通信時のエラー
    """
    url = f"https://expense.moneyforward.com/api/external/v1/offices/{OFFICE_ID}/me/ex_reports"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

@tool
def get_waiting_approvals() -> dict:
    """承認待ちの経費レポートの一覧を取得する

    Returns:
        dict: 承認待ちの経費レポートの一覧
    
    Raises:
        requests.exceptions.RequestException: API通信時のエラー
    """
    url = f"https://expense.moneyforward.com/api/external/v1/offices/{OFFICE_ID}/me/approving_ex_reports"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

@tool
def approve_expense(expense_id: str) -> dict:
    """経費レポートを承認する

    Args:
        expense_id (str): 承認する経費レポートのID

    Returns:
        dict: 承認結果
    
    Raises:
        requests.exceptions.RequestException: API通信時のエラー
    """
    url = f"https://expense.moneyforward.com/api/external/v1/offices/{OFFICE_ID}/ex_reports/{expense_id}/approve"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

tools = [upload_receipt_image, get_expense_reports, get_waiting_approvals, approve_expense]
tool_node = ToolNode(tools)