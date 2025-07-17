; ============================================================
;  Cheqory ��װ�ű�
;  ʹ�� NSIS 3.x + HM VNISEdit ��ģ��
;  ���ߣ�Aurorp1g
; ============================================================

; ��װ�����ʼ���峣��
!define PRODUCT_NAME "Cheqory"
!define PRODUCT_VERSION "1.0.0.0"
!define PRODUCT_PUBLISHER "Aurorp1g"
!define PRODUCT_WEB_SITE "https://github.com/Aurorp1g/Cheqory"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Cheqory.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; ------ MUI �ִ����涨�� (1.67 �汾���ϼ���) ------
!include "MUI.nsh"

; MUI Ԥ���峣��
!define MUI_ABORTWARNING
!define MUI_ICON "Cheqory\resources\logo.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; ��ӭҳ��
!insertmacro MUI_PAGE_WELCOME
; ��װĿ¼ѡ��ҳ��
!insertmacro MUI_PAGE_DIRECTORY
; ��װ����ҳ��
!insertmacro MUI_PAGE_INSTFILES
; ��װ���ҳ��
!define MUI_FINISHPAGE_RUN "$INSTDIR\Cheqory.exe"
!insertmacro MUI_PAGE_FINISH

; ��װж�ع���ҳ��
!insertmacro MUI_UNPAGE_INSTFILES

; ��װ�����������������
!insertmacro MUI_LANGUAGE "SimpChinese"

; ��װԤ�ͷ��ļ�
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI �ִ����涨����� ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Cheqory_Installer.exe"
InstallDir "$PROGRAMFILES\Cheqory"
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show
BrandingText " "

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File "Cheqory\Cheqory.exe"
  CreateDirectory "$SMPROGRAMS\Cheqory"
  CreateShortCut "$SMPROGRAMS\Cheqory\Cheqory.lnk" "$INSTDIR\Cheqory.exe"
  CreateShortCut "$DESKTOP\Cheqory.lnk" "$INSTDIR\Cheqory.exe"
  File /r "Cheqory\*.*"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\Cheqory\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\Cheqory\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Cheqory.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Cheqory.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

/******************************
 *  �����ǰ�װ�����ж�ز���  *
 ******************************/

Section Uninstall
  ; 1) ������ݹ�ɾ����װĿ¼
  RMDir /r "$INSTDIR"

  ; 2) ��ɾ��ݷ�ʽ�����Ŀ¼�Ѳ�����Ҳû���⣩
  Delete "$DESKTOP\Cheqory.lnk"
  Delete "$SMPROGRAMS\Cheqory\Cheqory.lnk"
  Delete "$SMPROGRAMS\Cheqory\Website.lnk"
  Delete "$SMPROGRAMS\Cheqory\Uninstall.lnk"
  RMDir  "$SMPROGRAMS\Cheqory"

  ; 3) ����ע���
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  SetAutoClose true
SectionEnd

#-- ���� NSIS �ű��༭�������� Function ���α�������� Section ����֮���д���Ա��ⰲװ�������δ��Ԥ֪�����⡣--#

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "��ȷʵҪ��ȫ�Ƴ� $(^Name) ���������е������" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) �ѳɹ��ش����ļ�����Ƴ���"
FunctionEnd
