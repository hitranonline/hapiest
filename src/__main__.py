import wx

app = wx.App(False)
frame = wx.Frame(None, wx.ID_ANY, "Hey")
frame.Show(True)
frame2 = wx.Frame(None, wx.ID_ANY, "Hey")
frame2.Show(True)
app.MainLoop()
