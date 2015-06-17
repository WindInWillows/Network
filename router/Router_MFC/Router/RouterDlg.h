
// RouterDlg.h : ͷ�ļ�
//

#pragma once


// CRouterDlg �Ի���
class CRouterDlg : public CDialogEx
{
// ����
public:
	CRouterDlg(CWnd* pParent = NULL);	// ��׼���캯��

// �Ի�������
	enum { IDD = IDD_ROUTER_DIALOG };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV ֧��


// ʵ��
protected:
	HICON m_hIcon;

	// ���ɵ���Ϣӳ�亯��
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnBnClickedButton3();
	afx_msg void OnStartClickedBtn();
	afx_msg void OnStopClickedBtn();
	afx_msg void OnAddClickedRouterBtn();
	afx_msg void OnDeleteClickedRouterBtn();
	afx_msg void OnTimer(UINT_PTR nIDEvent);
	afx_msg void OnDestroy();
	CListBox Logger;
	CListBox m_RouteTable;
	CIPAddressCtrl m_Destination;
	CIPAddressCtrl m_NextHop;
	CIPAddressCtrl m_Mask;
	CListBox m_MacIP;
};
