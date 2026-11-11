// Tracked arm vines and animated butterflies, drawn over the live flower scene.
uniform vec4 uGarden; // butterfly count, vines amount, mirror, seconds
uniform vec4 uBody; // body center x,y, tracking confidence, vine growth
uniform vec4 uLeftUpper; // shoulder xy, elbow xy
uniform vec4 uLeftLower; // wrist xy, valid, unused
uniform vec4 uRightUpper;
uniform vec4 uRightLower;
out vec4 fragColor;
float hash21(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
vec2 screenPoint(vec2 p){return vec2(uGarden.z>.5?1.-p.x:p.x,p.y);}
vec4 vine(vec2 p,vec2 a,vec2 b,float growth,float seed){
 vec2 ab=b-a; float len=length(ab); if(len<.01)return vec4(0.);
 vec2 axis=ab/len; vec2 normal=vec2(-axis.y,axis.x);
 float t=clamp(dot(p-a,axis)/len,0.,1.);
 float bend=sin(t*24.+seed+uGarden.w*.3)*.004;
 float distance=abs(dot(p-a,normal)-bend);
 float stem=(1.-smoothstep(.0014,.0035,distance))*step(t,growth)*step(0.,dot(p-a,axis))*step(dot(p-a,axis),len);
 vec3 color=vec3(.18,.54,.12); float alpha=stem;
 for(int j=0;j<8;j++){
  float along=(float(j)+.5)/8.; float side=mod(float(j),2.)*2.-1.;
  vec2 pos=a+ab*along+normal*sin(along*24.+seed+uGarden.w*.3)*.004;
  vec2 direction=normalize(axis*.55+normal*side);
  vec2 leafCenter=pos+direction*.011;
  vec2 q=p-leafCenter; float x=dot(q,direction)/.016;float y=dot(q,vec2(-direction.y,direction.x))/.006;
  float leaf=(1.-smoothstep(.8,1.,x*x+y*y))*smoothstep(along-.04,along+.04,growth);
  vec3 green=mix(vec3(.08,.28,.06),vec3(.4,.76,.18),clamp(.5+.5*y,0.,1.));
  if(leaf>alpha){color=green;alpha=leaf;}
 }
 return vec4(color,alpha);
}
vec4 butterfly(vec2 p,vec2 center,float angle,float phase,float scale,float hue){
 vec2 q=p-center; q=mat2(cos(angle),-sin(angle),sin(angle),cos(angle))*q;
 q/=scale;
 float flap=.2+.8*abs(sin(phase));
 q.x/=flap;
 float upper=pow((abs(q.x)-.48)/.48,2.)+pow((q.y-.20)/.52,2.);
 float lower=pow((abs(q.x)-.34)/.34,2.)+pow((q.y+.35)/.34,2.);
 float wing=min(upper,lower);
 float shape=1.-smoothstep(.85,1.05,wing);
 vec3 tone=mix(vec3(1.,.42,.06),vec3(.65,.3,1.),hue);
 tone*=.5+.5*(1.-clamp(wing,0.,1.));
 float spots=pow(abs(sin(q.y*16.+q.x*9.)),18.);
 tone=mix(tone,vec3(1.,.96,.7),spots*.6);
 tone=mix(tone,vec3(.045,.018,.025),smoothstep(.68,.98,wing));
 float body=1.-smoothstep(.065,.11,abs(q.x));body*=1.-smoothstep(.35,.5,abs(q.y));
 tone=mix(tone,vec3(.06,.025,.02),body);
 return vec4(tone,max(shape,body));
}
void main(){
 vec2 uv=vUV.st; vec3 scene=texture(sTD2DInputs[0],uv).rgb;
 float aspect=uTD2DInfos[0].res.z/uTD2DInfos[0].res.w;
 vec2 metric=vec2(aspect,1.);vec2 p=uv*metric;
 float growth=uBody.w;
 for(int side=0;side<2;side++){
  vec4 upper=side==0?uLeftUpper:uRightUpper; vec4 lower=side==0?uLeftLower:uRightLower;
  float enabled=uGarden.y*uBody.z*lower.z;
  vec2 a=screenPoint(upper.xy)*metric; vec2 b=screenPoint(upper.zw)*metric;vec2 d=screenPoint(lower.xy)*metric;
  vec4 v=vine(p,a,b,smoothstep(0.,.55,growth),float(side)*4.);
  scene=mix(scene,v.rgb,v.a*enabled);
  v=vine(p,b,d,smoothstep(.45,1.,growth),float(side)*4.+2.);
  scene=mix(scene,v.rgb,v.a*enabled);
 }
 vec2 center=screenPoint(uBody.xy);
 for(int i=0;i<12;i++){
  if(float(i)>=uGarden.x)break;
  float h=hash21(vec2(i,7.)); float time=uGarden.w*(.3+h*.15);
  float a=time+float(i)*2.39996;
  vec2 pos=center+vec2(cos(a)*(.20+.10*h)/aspect,sin(a*.83)*(.16+.12*h));
  pos+=vec2(sin(time*2.1+h*8.),cos(time*1.7+h*4.))*.025;
  float angle=sin(time+h*20.)*.7;
  vec4 b=butterfly(p,pos*metric,angle,uGarden.w*(7.+h*5.)+h*12.,.021+h*.011,h);
  scene=mix(scene,b.rgb,b.a);
 }
 fragColor=TDOutputSwizzle(vec4(scene,1.));
}
