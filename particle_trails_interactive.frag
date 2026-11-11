// Stateful GPU trails: contour petals emit, drift, and fade in a feedback buffer.
uniform vec4 uSim; // absolute time, lifetime, drift speed, particle size in px
uniform vec4 uAmount; // particle amount
uniform vec4 uHands; // left wrist xy, right wrist xy
uniform vec4 uReact; // burst, left valid, right valid, enabled
out vec4 fragColor;
float hash21(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float maskAt(vec2 uv){return texture(sTD2DInputs[1],uv).a;}
vec3 palette(float h){return mix(vec3(1.,.32,.48),vec3(1.,.82,.29),h);}
void main(){
 vec2 uv=vUV.st; vec2 res=uTD2DInfos[1].res.zw; vec2 px=1./res;
 float now=mod(uSim.x,10.);
 float then=texture(sTD2DInputs[0],vec2(.5)).a;
 float dt=clamp(mod(now-then+10.,10.),.004,.06);
 vec2 velocity=vec2(.013*sin(uv.y*12.+uSim.x*.7),.028)*uSim.z;
 for(int hand=0;hand<2;hand++){vec2 p=hand==0?uHands.xy:uHands.zw;float v=hand==0?uReact.y:uReact.z;vec2 d=uv-p;velocity+=normalize(d+vec2(.0001))*.14*uReact.x*v*exp(-length(d)*10.);}
 vec3 history=texture(sTD2DInputs[0],uv-velocity*dt).rgb;
 history*=exp(-dt*3./max(.15,uSim.y));
 vec2 grid=uv*res/24.; vec2 cell=floor(grid);
 vec3 emission=vec3(0.);
 for(int j=-1;j<=1;j++)for(int i=-1;i<=1;i++){
  vec2 id=cell+vec2(i,j); float h=hash21(id);
  float period=1.1+h*.9;
  float life=fract(uSim.x/period+h);
  vec2 center=(id+.5+vec2(hash21(id+3.),hash21(id+8.))*.45-.225)*24./res;
  float l=maskAt(center-vec2(12.*px.x,0.)); float r=maskAt(center+vec2(12.*px.x,0.));
  float b=maskAt(center-vec2(0.,12.*px.y)); float t=maskAt(center+vec2(0.,12.*px.y));
  float edge=clamp(max(max(l,r),max(b,t))-min(min(l,r),min(b,t)),0.,1.);
  vec2 outward=normalize(vec2(l-r,b-t)+vec2(.001,.002));
  vec2 drift=outward*life*.018*uSim.z+vec2(sin(life*6.+h*20.)*.008,life*.022)*uSim.z;
  drift*=1.+uReact.x*3.;
  vec2 q=(uv-center-drift)*res/max(1.,uSim.w);
  float spin=h*6.28+uSim.x*.8;
  q=mat2(cos(spin),-sin(spin),sin(spin),cos(spin))*q;
  float petal=exp(-dot(q*vec2(.65,1.8),q*vec2(.65,1.8))*2.2);
  float twinkle=.5+.5*sin(uSim.x*5.+h*25.);
  float emitGate=smoothstep(.08,.35,edge)*(1.-smoothstep(.5,.95,life));
  emitGate*=step(h,clamp(uAmount.x+uReact.x*.5,0.,1.));
  emission+=palette(h)*petal*emitGate*(.6+.4*twinkle)*1.4*(1.+uReact.x*2.);
 }
 for(int hand=0;hand<2;hand++)for(int k=0;k<12;k++){
  float h=hash21(vec2(k,hand+21.));float age=fract(uSim.x*(.5+h*.7)+h);
  vec2 wrist=hand==0?uHands.xy:uHands.zw;float valid=hand==0?uReact.y:uReact.z;
  float angle=h*6.28318+sin(uSim.x+h*10.)*.2;
  vec2 center=wrist+vec2(cos(angle),sin(angle))*(.006+age*.12*(1.+uReact.x));
  vec2 q=(uv-center)*res/max(1.,uSim.w*1.2);
  float petal=exp(-dot(q*vec2(.7,1.5),q*vec2(.7,1.5)));
  emission+=palette(h)*petal*valid*uReact.x*(1.-age)*2.;
 }
 vec3 particles=max(history,emission);
 fragColor=TDOutputSwizzle(vec4(particles,now));
}
