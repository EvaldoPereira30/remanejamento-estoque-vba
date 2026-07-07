Attribute VB_Name = "Módulo2"
Sub Importar_Estoque_Filiais()

    Dim arquivo As Variant
    Dim wsDestino As Worksheet
    Dim wbOrigem As Workbook
    Dim wsOrigem As Worksheet
    Dim ultLinha As Long
    
    arquivo = Application.GetOpenFilename( _
        FileFilter:="Arquivos Excel (*.xls; *.xlsx), *.xls; *.xlsx", _
        Title:="Selecione o arquivo - Estoque Filiais")
    
    If arquivo = False Then Exit Sub
    
    Application.ScreenUpdating = False
    
    On Error Resume Next
    Set wsDestino = ThisWorkbook.Sheets("Estoque Filiais")
    On Error GoTo 0
    
    If wsDestino Is Nothing Then
        Set wsDestino = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        wsDestino.Name = "Estoque Filiais"
    Else
        wsDestino.Cells.Clear
    End If
    
    Set wbOrigem = Workbooks.Open(Filename:=arquivo)
    Set wsOrigem = wbOrigem.Sheets(1)
    
    wsOrigem.UsedRange.Copy Destination:=wsDestino.Range("A1")
    wbOrigem.Close SaveChanges:=False
    
    Call Ajustar_Estoque_Filiais_Importado(wsDestino)
    
    Call Preencher_Filial_Em_Branco(wsDestino)
    
    ultLinha = wsDestino.Cells(wsDestino.Rows.Count, "B").End(xlUp).Row
    
    If ultLinha < 2 Then
        Application.ScreenUpdating = True
        MsgBox "O arquivo importado não possui dados.", vbExclamation
        Exit Sub
    End If
    
    Call Calcular_Colunas_Estoque_Filiais
    Call Atualizar_Indicadores_Painel
    
    Application.ScreenUpdating = True
    
    ThisWorkbook.Sheets("Painel").Activate
    
    MsgBox "Estoque Filiais importado com sucesso!" & vbCrLf & _
           "Linhas importadas: " & ultLinha - 1, vbInformation

End Sub

Sub Calcular_Colunas_Estoque_Filiais()

    Dim ws As Worksheet
    Dim wsPainel As Worksheet
    Dim ultLinha As Long
    Dim i As Long
    Dim media30 As Double
    Dim estoque As Double
    Dim diasAtual As Double
    Dim estoqueMax As Double
    Dim capacidade As Double
    Dim diasAlvo As Double
    
    Set ws = ThisWorkbook.Sheets("Estoque Filiais")
    Set wsPainel = ThisWorkbook.Sheets("Painel")
    
    diasAlvo = wsPainel.Range("J7").Value
    
    If diasAlvo <= 0 Then
        MsgBox "Informe um valor válido em Dias Alvo no Painel.", vbExclamation
        Exit Sub
    End If
    
    ultLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    ws.Range("J:M").Clear
    
    ws.Range("J1").Value = "Dias Estoque Atual"
    ws.Range("K1").Value = "Estoque Máx " & diasAlvo & " dias"
    ws.Range("L1").Value = "Capacidade " & diasAlvo & " dias"
    ws.Range("M1").Value = "Status Absorção"
    
    For i = 2 To ultLinha
        
        media30 = Val(ws.Cells(i, "H").Value)
        estoque = Val(ws.Cells(i, "I").Value)
        
        If media30 > 0 Then
            
            diasAtual = estoque / (media30 / 30)
            estoqueMax = (media30 / 30) * diasAlvo
            capacidade = Application.Max(0, estoqueMax - estoque)
            
        Else
            
            diasAtual = 0
            estoqueMax = 0
            capacidade = 0
            
        End If
        
        ws.Cells(i, "J").Value = diasAtual
        ws.Cells(i, "K").Value = estoqueMax
        ws.Cells(i, "L").Value = capacidade
        
        If media30 <= 0 Then
            
            ws.Cells(i, "M").Value = "Sem Média"
            
        ElseIf diasAtual >= diasAlvo Then
            
            ws.Cells(i, "M").Value = "Não Absorve"
            
        Else
            
            ws.Cells(i, "M").Value = "Pode Absorver"
            
        End If
        
    Next i
    
    With ws
        
        .Rows.RowHeight = 18
        .Rows(1).RowHeight = 35
        
        .Range("A1:M1").Font.Bold = True
        .Range("A1:M1").HorizontalAlignment = xlCenter
        .Range("A1:M1").VerticalAlignment = xlCenter
        .Range("A1:M1").Interior.Color = RGB(155, 194, 230)
        
        .Columns("A").ColumnWidth = 8
        .Columns("B").ColumnWidth = 10
        .Columns("C").ColumnWidth = 16
        .Columns("D").ColumnWidth = 35
        .Columns("E").ColumnWidth = 14
        .Columns("F").ColumnWidth = 14
        .Columns("G").ColumnWidth = 14
        .Columns("H").ColumnWidth = 10
        .Columns("I").ColumnWidth = 12
        
        .Columns("J").ColumnWidth = 15
        .Columns("K").ColumnWidth = 18
        .Columns("L").ColumnWidth = 18
        .Columns("M").ColumnWidth = 16
        
        .Range("A:M").VerticalAlignment = xlCenter
        
        .Range("A:C").HorizontalAlignment = xlCenter
        .Range("E:M").HorizontalAlignment = xlCenter
        
        .Range("D:D").HorizontalAlignment = xlLeft
        
        .Range("A:M").WrapText = False
        .Rows(1).WrapText = True
        
        .Range("H:L").NumberFormat = "0.00"
        
        .Range("A:B").NumberFormat = "0"
        .Range("C:C").NumberFormat = "0"
        
    End With

End Sub


Sub Importar_Excesso()

    Dim arquivo As Variant
    Dim wsDestino As Worksheet
    Dim wbOrigem As Workbook
    Dim wsOrigem As Worksheet
    Dim ultLinha As Long
    
    arquivo = Application.GetOpenFilename( _
        FileFilter:="Arquivos Excel (*.xls; *.xlsx), *.xls; *.xlsx", _
        Title:="Selecione o arquivo - Excesso")
    
    If arquivo = False Then Exit Sub
    
    Application.ScreenUpdating = False
    
    On Error Resume Next
    Set wsDestino = ThisWorkbook.Sheets("Excesso")
    On Error GoTo 0
    
    If wsDestino Is Nothing Then
        Set wsDestino = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        wsDestino.Name = "Excesso"
    Else
        wsDestino.Cells.Clear
    End If
    
    Set wbOrigem = Workbooks.Open(Filename:=arquivo)
    Set wsOrigem = wbOrigem.Sheets(1)
    
    wsOrigem.UsedRange.Copy Destination:=wsDestino.Range("A1")
    
    wbOrigem.Close SaveChanges:=False
    
    Call Ajustar_Excesso_Importado(wsDestino)
    Call Preencher_Filial_Em_Branco(wsDestino)
    
    If Not Validar_Layout_Excesso(wsDestino) Then
        Application.DisplayAlerts = False
        wsDestino.Delete
        Application.DisplayAlerts = True
        Application.ScreenUpdating = True
        ThisWorkbook.Sheets("Painel").Activate
        Exit Sub
    End If
    
    ultLinha = wsDestino.Cells(wsDestino.Rows.Count, "B").End(xlUp).Row
    
    If ultLinha < 2 Then
        Application.ScreenUpdating = True
        MsgBox "O arquivo importado não possui dados.", vbExclamation
        Exit Sub
    End If
    
    wsDestino.Columns("A:D").AutoFit
    
    Application.ScreenUpdating = True
    
    With ThisWorkbook.Sheets("Painel")
    .Range("J10").Value = ultLinha - 1
    .Range("J11").Value = Now
    .Range("J11").NumberFormat = "dd/mm/yyyy hh:mm"
    End With
    
    Call Atualizar_Indicadores_Painel
    
    ThisWorkbook.Sheets("Painel").Activate
    
    MsgBox "Excesso importado com sucesso!" & vbCrLf & _
           "Linhas importadas: " & ultLinha - 1, vbInformation

End Sub
Sub Gerar_Sugestao_Remanejamento()

    Dim wsEx As Worksheet, wsEst As Worksheet, wsOut As Worksheet, wsPainel As Worksheet
    Dim ultEx As Long, ultEst As Long, linhaOut As Long
    Dim i As Long, j As Long, rodada As Long
    Dim lojaOrigem As String, codProduto As String, descricao As String
    Dim qtdExcesso As Double, saldo As Double, estoqueOrigem As Double
    Dim lojaDestino As String
    Dim diasAtual As Double, capacidade As Double
    Dim media30 As Double, estoqueAtual As Double
    Dim qtdEnviar As Double, diasApos As Double
    Dim diasAlvo As Double
    
    Set wsEx = ThisWorkbook.Sheets("Excesso")
    Set wsEst = ThisWorkbook.Sheets("Estoque Filiais")
    Set wsPainel = ThisWorkbook.Sheets("Painel")
    
    diasAlvo = wsPainel.Range("J7").Value
    
    If diasAlvo <= 0 Then
        MsgBox "Informe um valor válido em Dias Alvo no Painel.", vbExclamation
        Exit Sub
    End If
    
    On Error Resume Next
    Set wsOut = ThisWorkbook.Sheets("Sugestão_Remanejamento")
    On Error GoTo 0
    
    If wsOut Is Nothing Then
        Set wsOut = ThisWorkbook.Sheets.Add(After:=wsEst)
        wsOut.Name = "Sugestão_Remanejamento"
    Else
        wsOut.Cells.Clear
    End If
    
    wsOut.Range("A1:J1").Value = Array("Origem", "Produto", "Descrição", "Qtde Excesso", "Destino", _
                                       "Dias Atual Destino", "Capacidade Dias Alvo", "Qtde Sugerida", _
                                       "Dias Após", "Saldo Restante")
    
    ultEx = wsEx.Cells(wsEx.Rows.Count, "A").End(xlUp).Row
    ultEst = wsEst.Cells(wsEst.Rows.Count, "A").End(xlUp).Row
    linhaOut = 2
    
    'Ordena por produto e maior MediaF
    With wsEst.Sort
        .SortFields.Clear
        .SortFields.Add Key:=wsEst.Range("B2:B" & ultEst), Order:=xlAscending
        .SortFields.Add Key:=wsEst.Range("H2:H" & ultEst), Order:=xlDescending
        .SetRange wsEst.Range("A1:M" & ultEst)
        .Header = xlYes
        .Apply
    End With
    
    For i = 2 To ultEx
        
        lojaOrigem = Trim(wsEx.Cells(i, "A").Value)
        codProduto = Trim(wsEx.Cells(i, "B").Value)
        descricao = wsEx.Cells(i, "C").Value
        qtdExcesso = wsEx.Cells(i, "D").Value
        
        estoqueOrigem = Estoque_Origem_Disponivel(wsEst, lojaOrigem, codProduto)
        
        If estoqueOrigem <= 0 Then
            saldo = 0
        Else
            saldo = WorksheetFunction.Min(qtdExcesso, estoqueOrigem)
        End If
        
        If saldo > 0 Then
            
            For rodada = 1 To 2
                
                For j = 2 To ultEst
                    
                    If saldo <= 0 Then Exit For
                    
                    If Trim(wsEst.Cells(j, "B").Value) = codProduto _
                       And Trim(wsEst.Cells(j, "A").Value) <> lojaOrigem Then
                        
                        lojaDestino = wsEst.Cells(j, "A").Value
                        media30 = wsEst.Cells(j, "H").Value
                        estoqueAtual = wsEst.Cells(j, "I").Value
                        
                        If media30 > 0 Then
                            diasAtual = estoqueAtual / (media30 / 30)
                            capacidade = ((media30 / 30) * diasAlvo) - estoqueAtual
                        Else
                            diasAtual = 0
                            capacidade = 0
                        End If
                        
                        If capacidade > 0 Then
                            
                            qtdEnviar = 0
                            
                            'Rodada 1: lojas com estoque zerado recebem 1 unidade
                            If rodada = 1 And estoqueAtual <= 0 Then
                                qtdEnviar = WorksheetFunction.Min(saldo, capacidade, 1)
                            End If
                            
                            'Rodada 2: saldo restante vai para maiores médias
                            If rodada = 2 And estoqueAtual > 0 Then
                                qtdEnviar = WorksheetFunction.Min(saldo, capacidade)
                            End If
                            
                            If qtdEnviar > 0 Then
                                
                                diasApos = (estoqueAtual + qtdEnviar) / (media30 / 30)
                                saldo = saldo - qtdEnviar
                                
                                wsOut.Cells(linhaOut, "A").Value = lojaOrigem
                                wsOut.Cells(linhaOut, "B").Value = codProduto
                                wsOut.Cells(linhaOut, "C").Value = descricao
                                wsOut.Cells(linhaOut, "D").Value = qtdExcesso
                                wsOut.Cells(linhaOut, "E").Value = lojaDestino
                                wsOut.Cells(linhaOut, "F").Value = diasAtual
                                wsOut.Cells(linhaOut, "G").Value = capacidade
                                wsOut.Cells(linhaOut, "H").Value = qtdEnviar
                                wsOut.Cells(linhaOut, "I").Value = diasApos
                                wsOut.Cells(linhaOut, "J").Value = saldo
                                
                                linhaOut = linhaOut + 1
                                
                            End If
                            
                        End If
                        
                    End If
                    
                Next j
                
            Next rodada
            
            If saldo > 0 Then
                wsOut.Cells(linhaOut, "A").Value = lojaOrigem
                wsOut.Cells(linhaOut, "B").Value = codProduto
                wsOut.Cells(linhaOut, "C").Value = descricao
                wsOut.Cells(linhaOut, "D").Value = qtdExcesso
                wsOut.Cells(linhaOut, "E").Value = "Sem loja destino"
                wsOut.Cells(linhaOut, "J").Value = saldo
                linhaOut = linhaOut + 1
            End If
            
        End If
        
    Next i
    
    wsOut.Columns("A:J").AutoFit
    
    Call Gerar_Remanejamento_Final
    
    ThisWorkbook.Sheets("Painel").Activate
    
    MsgBox "Sugestão de remanejamento gerada com sucesso!", vbInformation

End Sub

Function Estoque_Origem_Disponivel(wsEst As Worksheet, lojaOrigem As String, codProduto As String) As Double

    Dim ultLinha As Long
    Dim i As Long
    Dim lojaEst As String
    Dim prodEst As String
    
    ultLinha = wsEst.Cells(wsEst.Rows.Count, "A").End(xlUp).Row
    
    For i = 2 To ultLinha
        
        lojaEst = Trim(CStr(wsEst.Cells(i, "A").Value))
        prodEst = Trim(CStr(wsEst.Cells(i, "B").Value))
        
        If lojaEst = Trim(CStr(lojaOrigem)) _
           And prodEst = Trim(CStr(codProduto)) Then
            
            Estoque_Origem_Disponivel = wsEst.Cells(i, "I").Value
            Exit Function
            
        End If
        
    Next i
    
    Estoque_Origem_Disponivel = 0

End Function

Sub Gerar_Remanejamento_Final()

    Dim wsSug As Worksheet, wsFinal As Worksheet
    Dim ultLinha As Long, linhaFinal As Long
    Dim i As Long
    
    Set wsSug = ThisWorkbook.Sheets("Sugestão_Remanejamento")
    
    On Error Resume Next
    Set wsFinal = ThisWorkbook.Sheets("Final - Importar")
    On Error GoTo 0
    
    If wsFinal Is Nothing Then
        Set wsFinal = ThisWorkbook.Sheets.Add(After:=wsSug)
        wsFinal.Name = "Final - Importar"
    Else
        wsFinal.Cells.Clear
    End If
    
    wsFinal.Tab.Color = RGB(0, 176, 80)
    
    wsFinal.Range("A1:E1").Value = Array("Destino", "Origem", "Produto", "Descrição", "Qtde Enviar")
    
    ultLinha = wsSug.Cells(wsSug.Rows.Count, "A").End(xlUp).Row
    linhaFinal = 2
    
    For i = 2 To ultLinha
        
        If wsSug.Cells(i, "E").Value <> "Sem loja destino" _
            And WorksheetFunction.Round(wsSug.Cells(i, "H").Value, 0) > 0 Then
            
            wsFinal.Cells(linhaFinal, "A").Value = wsSug.Cells(i, "E").Value   'Destino
            wsFinal.Cells(linhaFinal, "B").Value = wsSug.Cells(i, "A").Value   'Origem
            wsFinal.Cells(linhaFinal, "C").Value = wsSug.Cells(i, "B").Value   'Produto
            wsFinal.Cells(linhaFinal, "D").Value = wsSug.Cells(i, "C").Value   'Descrição
            wsFinal.Cells(linhaFinal, "E").Value = WorksheetFunction.Round(wsSug.Cells(i, "H").Value, 0) 'Qtde Enviar
            linhaFinal = linhaFinal + 1
            
        End If
        
    Next i
    
    With wsFinal.Sort
    .SortFields.Clear
    
    .SortFields.Add Key:=wsFinal.Range("A2:A" & linhaFinal - 1), _
                    SortOn:=xlSortOnValues, _
                    Order:=xlAscending, _
                    DataOption:=xlSortNormal
                    
    .SortFields.Add Key:=wsFinal.Range("B2:B" & linhaFinal - 1), _
                    SortOn:=xlSortOnValues, _
                    Order:=xlAscending, _
                    DataOption:=xlSortNormal
    
    .SetRange wsFinal.Range("A1:E" & linhaFinal - 1)
    .Header = xlYes
    .Apply
End With
    
    wsFinal.Columns("A:E").AutoFit

End Sub

Sub Limpar_Tudo_Remanejamento()

    Dim ws As Worksheet
    Dim resposta As VbMsgBoxResult
    
    resposta = MsgBox( _
        "Deseja realmente limpar todos os dados e remover as abas geradas?", _
        vbQuestion + vbYesNo, _
        "Confirmar Limpeza")
    
    If resposta = vbNo Then Exit Sub
    
    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    
    On Error Resume Next
    
    Set ws = ThisWorkbook.Sheets("Estoque Filiais")
    If Not ws Is Nothing Then ws.Delete
    
    Set ws = Nothing
    Set ws = ThisWorkbook.Sheets("Excesso")
    If Not ws Is Nothing Then ws.Delete
    
    Set ws = Nothing
    Set ws = ThisWorkbook.Sheets("Sugestão_Remanejamento")
    If Not ws Is Nothing Then ws.Delete
    
    Set ws = Nothing
    Set ws = ThisWorkbook.Sheets("Final - Importar")
    If Not ws Is Nothing Then ws.Delete
    
    On Error GoTo 0
    
    With ThisWorkbook.Sheets("Painel")
        .Range("J7").Value = 90
        .Range("J9").Value = 0
        .Range("J10").Value = 0
        .Range("J12").Value = "-"
        End With
    
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
    
    MsgBox "Limpeza concluída com sucesso!", vbInformation

End Sub


Sub Exportar_Remanejamento_TXT()

    Dim ws As Worksheet
    Dim ultLinha As Long, i As Long
    Dim pasta As String
    Dim destino As String, origem As String, produto As String, qtde As String
    Dim dict As Object
    Dim chave As Variant
    Dim arquivo As Integer
    Dim caminhoArquivo As String
    Dim linhaTXT As String
    
    Set ws = ThisWorkbook.Sheets("Final - Importar")
    Set dict = CreateObject("Scripting.Dictionary")
    
    ultLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    If ultLinha < 2 Then
        MsgBox "Não há dados na aba Remanejamento Final para exportar.", vbExclamation
        Exit Sub
    End If
    
    With Application.FileDialog(msoFileDialogFolderPicker)
        .Title = "Selecione a pasta para salvar os arquivos TXT"
        
        If .Show <> -1 Then Exit Sub
        
        pasta = .SelectedItems(1)
    End With
    
    For i = 2 To ultLinha
        destino = Trim(ws.Cells(i, "A").Value)
        
        If destino <> "" Then
            If Not dict.Exists(destino) Then
                dict.Add destino, ""
            End If
        End If
    Next i
    
    For Each chave In dict.Keys
        
        caminhoArquivo = pasta & "\Remanejar Filial " & chave & ".txt"
        arquivo = FreeFile
        
        Open caminhoArquivo For Output As #arquivo
                      
        For i = 2 To ultLinha
            
            destino = Trim(ws.Cells(i, "A").Value)
            
            If destino = chave Then
                
                origem = Trim(ws.Cells(i, "B").Value)
                produto = Trim(ws.Cells(i, "C").Value)
                qtde = Trim(ws.Cells(i, "E").Value)
                
                linhaTXT = origem & ";" & produto & ";" & qtde
                
                Print #arquivo, linhaTXT
                
            End If
            
        Next i
        
        Close #arquivo
        
    Next chave
    
    ThisWorkbook.Sheets("Painel").Activate
    
    MsgBox "Arquivos TXT exportados com sucesso!", vbInformation

End Sub


Sub Ajustar_Estoque_Filiais_Importado(ws As Worksheet)

    Dim ultLinha As Long
    Dim i As Long
    
    ws.Cells.UnMerge
    
    ws.Rows("1:2").Delete
    
    ultLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    For i = ultLinha To 2 Step -1
        
        If InStr(1, ws.Cells(i, "A").Value, "H:", vbTextCompare) > 0 _
           Or InStr(1, ws.Cells(i, "A").Value, "Usuário:", vbTextCompare) > 0 Then
            
            ws.Rows(i).Delete
            
        End If
        
    Next i

End Sub


Sub Preencher_Filial_Em_Branco(ws As Worksheet)

    Dim ultLinha As Long
    Dim i As Long
    Dim filialAtual As String
    
    ultLinha = ws.Cells(ws.Rows.Count, "B").End(xlUp).Row
    
    For i = 2 To ultLinha
        
        If Trim(ws.Cells(i, "A").Value) <> "" Then
            filialAtual = Trim(ws.Cells(i, "A").Value)
        Else
            ws.Cells(i, "A").Value = filialAtual
        End If
        
    Next i

End Sub


Sub Ajustar_Excesso_Importado(ws As Worksheet)

    Dim ultLinha As Long
    Dim i As Long
    Dim linhaCab As Long
    
    ws.Cells.UnMerge
    
    ultLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    For i = 1 To ultLinha
        If InStr(1, ws.Cells(i, "A").Value, "CodFilial", vbTextCompare) > 0 Then
            linhaCab = i
            Exit For
        End If
    Next i
    
    If linhaCab > 1 Then
        ws.Rows("1:" & linhaCab - 1).Delete
    End If
    
    ultLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    For i = ultLinha To 2 Step -1
        If InStr(1, ws.Cells(i, "A").Value, "H:", vbTextCompare) > 0 _
           Or InStr(1, ws.Cells(i, "A").Value, "Usuário:", vbTextCompare) > 0 Then
            ws.Rows(i).Delete
        End If
    Next i

End Sub

Function Validar_Layout_Excesso(ws As Worksheet) As Boolean

    Dim msg As String
    
    Validar_Layout_Excesso = False
    
    If Trim(ws.Range("A2").Value) = "" Or Not IsNumeric(ws.Range("A2").Value) Then
        msg = msg & "- Coluna A deve conter a filial na linha 2." & vbCrLf
    End If
    
    If Trim(ws.Range("B2").Value) = "" Or Not IsNumeric(ws.Range("B2").Value) Then
        msg = msg & "- Coluna B deve conter o código do produto na linha 2." & vbCrLf
    End If
    
    If Trim(ws.Range("C2").Value) = "" Or IsNumeric(ws.Range("C2").Value) Then
        msg = msg & "- Coluna C deve conter a descrição do produto na linha 2." & vbCrLf
    End If
    
    If Trim(ws.Range("D2").Value) = "" Or Not IsNumeric(ws.Range("D2").Value) Then
        msg = msg & "- Coluna D deve conter a quantidade na linha 2." & vbCrLf
    End If
    
    If Trim(ws.Range("E2").Value) <> "" Then
        msg = msg & "- Coluna E deve estar vazia. A quantidade parece ter sido deslocada para outra coluna." & vbCrLf
    End If
    
    If msg <> "" Then
        MsgBox "Layout inválido no arquivo de Excesso." & vbCrLf & vbCrLf & _
               "O layout esperado é:" & vbCrLf & _
               "Coluna A: Filial" & vbCrLf & _
               "Coluna B: Produto" & vbCrLf & _
               "Coluna C: Descrição" & vbCrLf & _
               "Coluna D: Quantidade" & vbCrLf & vbCrLf & _
               "Erros encontrados:" & vbCrLf & msg, _
               vbCritical, "Erro de Layout - Excesso"
        Exit Function
    End If
    
    Validar_Layout_Excesso = True

End Function

