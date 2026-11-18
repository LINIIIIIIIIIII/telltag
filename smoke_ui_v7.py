"""Fake Streamlit run; catches Python app wiring errors but not browser issues."""
import sys,types,runpy,os
class S(dict):
 def __getattr__(self,k):return self[k]
 def __setattr__(self,k,v):self[k]=v
class UI(types.ModuleType):
 def __init__(self):super().__init__('streamlit');self.session_state=S();self.sidebar=self
 def __enter__(self):return self
 def __exit__(self,*x):return False
 def __getattr__(self,n):
  if n in {'info','warning','error','success','markdown','caption','title','header','subheader','metric','plotly_chart','dataframe','write','divider','download_button','code','set_page_config'}:return lambda *a,**k:None
  if n in {'expander','container'}:return lambda *a,**k:self
  if n=='columns':return lambda count,**k:[self for _ in range(count if isinstance(count,int) else len(count))]
  if n=='tabs':return lambda names:[self for _ in names]
  if n=='checkbox':return lambda label,value=False,*a,**k:value
  if n=='radio':return lambda label,options,index=0,*a,**k:options[index]
  if n=='selectbox':
   def f(label, options,index=0,*a,**k):
    key=k.get('key');v=self.session_state.get(key,options[index]) if key else options[index]
    if label=='Choose food' and os.environ.get('V7_FOOD') in options:v=os.environ['V7_FOOD']
    if label=='Indicator' and os.environ.get('V7_INDICATOR') in options:v=os.environ['V7_INDICATOR']
    if key:self.session_state[key]=v
    return v
   return f
  if n=='file_uploader':return lambda *a,**k:None
  if n=='button':return lambda *a,**k:False
  if n=='slider':
   def f(label,*a,**k):
    result=k.get('value') if 'value' in k else (a[2] if len(a)>2 else a[0]);key=k.get('key');
    if key:self.session_state[key]=self.session_state.get(key,result);return self.session_state[key]
    return result
   return f
  if n=='number_input':
   def f(label,*a,**k):
    key=k.get('key')
    if key and key in self.session_state:return self.session_state[key]
    result=k.get('value',a[2] if len(a)>=3 else a[1] if len(a)>=2 else a[0] if a else 0)
    if key:self.session_state[key]=result
    return result
   return f
  if n=='color_picker':
   def f(label,value=None,*a,**k):
    key=k.get('key');result=self.session_state.get(key,value or '#000000') if key else value or '#000000'
    if key:self.session_state[key]=result
    return result
   return f
  raise AttributeError(n)
st=UI();sys.modules['streamlit']=st
comp=types.ModuleType('streamlit.components');v1=types.ModuleType('streamlit.components.v1');v1.html=lambda *a,**k:None;comp.v1=v1
sys.modules['streamlit.components']=comp;sys.modules['streamlit.components.v1']=v1
sys.path.insert(0,os.path.dirname(__file__))
runpy.run_path(os.path.join(os.path.dirname(__file__),'app.py'),run_name='__main__')
print('V7 MOCK STREAMLIT UI EXECUTED ALL FIVE TABS')
