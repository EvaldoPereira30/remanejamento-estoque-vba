Attribute VB_Name = "Módulo1"
Sub Criar_Painel_Remanejamento()

    Dim ws As Worksheet
    Dim btn As Button
    Dim nomes, macros
    Dim i As Long
    Dim topPos As Double
    
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("Painel")
    On Error GoTo 0
    
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Sheets.Add(Before:=ThisWorkbook.Sheets(1))
        ws.Name = "Painel"
    Else
        ws.Cells.Clear
        ws.Buttons.Delete
    End If
    
    ws.Activate
    ActiveWindow.DisplayGridlines = False
    
    ws.Cells.Interior.Color = RGB(218, 233, 248)
    ws.Columns("A:N").ColumnWidth = 10
    ws.Rows.RowHeight = 20
    
    'Cabeçalho
    With ws.Range("B2:M3")
        .Merge
        .Value = "REMANEJAMENTO DE ESTOQUE"
        .Interior.Color = RGB(31, 78, 121)
        .Font.Color = vbWhite
        .Font.Bold = True
        .Font.Size = 16
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
    End With
    
    'Linha separadora
    With ws.Range("B4:M4")
        .Interior.Color = RGB(200, 200, 200)
        .RowHeight = 3
    End With
    
    'Caixa Ações
    With ws.Range("B5:F14")
        .Interior.Color = RGB(242, 242, 242)
        .BorderAround LineStyle:=xlContinuous, Weight:=xlThin, Color:=RGB(191, 191, 191)
    End With
    
    With ws.Range("B5:F5")
        .Merge
        .Value = "AÇÕES"
        .Interior.Color = RGB(217, 225, 242)
        .Font.Bold = True
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
    End With
    
    'Caixa Parâmetros
    With ws.Range("H5:M14")
        .Interior.Color = RGB(242, 242, 242)
        .BorderAround LineStyle:=xlContinuous, Weight:=xlThin, Color:=RGB(191, 191, 191)
    End With
    
    With ws.Range("H5:M5")
        .Merge
        .Value = "PARÂMETROS"
        .Interior.Color = RGB(217, 225, 242)
        .Font.Bold = True
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
    End With
    
    'Dias Alvo
    ws.Range("H7").Value = "Dias Alvo"
    ws.Range("H7").Font.Bold = True
    
    With ws.Range("J7:K7")
        .Merge
        .Value = 90
        .Interior.Color = RGB(255, 242, 204)
        .Font.Bold = True
        .Font.Size = 12
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
        .BorderAround LineStyle:=xlContinuous, Weight:=xlMedium, Color:=RGB(191, 191, 191)
    End With
    
    'Indicadores
    ws.Range("H9").Value = "Estoque Filiais:"
    ws.Range("J9").Value = 0
    
    ws.Range("H10").Value = "Excesso:"
    ws.Range("J10").Value = 0
    
    ws.Range("H12").Value = "Última Atualização:"
    ws.Range("J12").Value = "-"
    
    'Botões
    nomes = Array( _
        "Importar Estoque Filiais", _
        "Importar Excesso", _
        "Gerar Sugestão", _
        "Exportar TXT", _
        "Limpar Tudo" _
    )
    
    macros = Array( _
        "Importar_Estoque_Filiais", _
        "Importar_Excesso", _
        "Gerar_Sugestao_Remanejamento", _
        "Exportar_Remanejamento_TXT", _
        "Limpar_Tudo_Remanejamento" _
    )
   Dim leftBtn As Double
   Dim larguraBtn As Double
    
    larguraBtn = 170
    
    leftBtn = ws.Range("B6:F14").Left + _
              (ws.Range("B6:F14").Width - larguraBtn) / 2
    
    topPos = ws.Range("C7").Top
    
    For i = LBound(nomes) To UBound(nomes)
    
        Set btn = ws.Buttons.Add(leftBtn, topPos, larguraBtn, 22)

    With btn
        .Caption = nomes(i)
        .OnAction = macros(i)
        .Font.Bold = True
    End With

    topPos = topPos + 28

Next i
    
    ws.Range("B2:M13").Font.Name = "Calibri"
    ws.Range("B2:M13").VerticalAlignment = xlCenter
    
    MsgBox "Painel criado com sucesso!", vbInformation

End Sub


Sub Atualizar_Indicadores_Painel()

    Dim wsPainel As Worksheet
    Dim wsEst As Worksheet
    Dim wsEx As Worksheet
    Dim dictAptas As Object
    Dim dictExcesso As Object
    Dim ultLinha As Long
    Dim i As Long
    Dim loja As String
    
    Set wsPainel = ThisWorkbook.Sheets("Painel")
    Set dictAptas = CreateObject("Scripting.Dictionary")
    Set dictExcesso = CreateObject("Scripting.Dictionary")
    
    On Error Resume Next
    Set wsEst = ThisWorkbook.Sheets("Estoque Filiais")
    Set wsEx = ThisWorkbook.Sheets("Excesso")
    On Error GoTo 0
    
    'Lojas Aptas
    If Not wsEst Is Nothing Then
        
        ultLinha = wsEst.Cells(wsEst.Rows.Count, "A").End(xlUp).Row
        
        For i = 2 To ultLinha
            
            loja = Trim(wsEst.Cells(i, "A").Value)
            
            If loja <> "" And wsEst.Cells(i, "M").Value = "Pode Absorver" Then
                If Not dictAptas.Exists(loja) Then
                    dictAptas.Add loja, 1
                End If
            End If
            
        Next i
        
    End If
    
    'Lojas Excesso
    If Not wsEx Is Nothing Then
        
        ultLinha = wsEx.Cells(wsEx.Rows.Count, "A").End(xlUp).Row
        
        For i = 2 To ultLinha
            
            loja = Trim(wsEx.Cells(i, "A").Value)
            
            If loja <> "" Then
                If Not dictExcesso.Exists(loja) Then
                    dictExcesso.Add loja, 1
                End If
            End If
            
        Next i
        
    End If
    
    With wsPainel
    
        .Range("J9").Value = dictAptas.Count
        .Range("J10").Value = dictExcesso.Count
    
        .Range("J12").Value = Now
        .Range("J12").NumberFormat = "dd/mm/yyyy hh:mm"
    
        .Columns("J").ColumnWidth = 22
    
    End With
    
End Sub
