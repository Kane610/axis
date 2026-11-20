var st=globalThis,lt=st.ShadowRoot&&(st.ShadyCSS===void 0||st.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Mt=Symbol(),oe=new WeakMap,Y=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==Mt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(lt&&t===void 0){let i=e!==void 0&&e.length===1;i&&(t=oe.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&oe.set(e,t))}return t}toString(){return this.cssText}},ie=o=>new Y(typeof o=="string"?o:o+"",void 0,Mt),v=(o,...t)=>{let e=o.length===1?o[0]:t.reduce((i,a,r)=>i+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(a)+o[r+1],o[0]);return new Y(e,o,Mt)},ae=(o,t)=>{if(lt)o.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let i=document.createElement("style"),a=st.litNonce;a!==void 0&&i.setAttribute("nonce",a),i.textContent=e.cssText,o.appendChild(i)}},kt=lt?o=>o:o=>o instanceof CSSStyleSheet?(t=>{let e="";for(let i of t.cssRules)e+=i.cssText;return ie(e)})(o):o;var{is:ho,defineProperty:mo,getOwnPropertyDescriptor:uo,getOwnPropertyNames:po,getOwnPropertySymbols:fo,getPrototypeOf:vo}=Object,ct=globalThis,re=ct.trustedTypes,go=re?re.emptyScript:"",wo=ct.reactiveElementPolyfillSupport,K=(o,t)=>o,G={toAttribute(o,t){switch(t){case Boolean:o=o?go:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,t){let e=o;switch(t){case Boolean:e=o!==null;break;case Number:e=o===null?null:Number(o);break;case Object:case Array:try{e=JSON.parse(o)}catch{e=null}}return e}},dt=(o,t)=>!ho(o,t),ne={attribute:!0,type:String,converter:G,reflect:!1,useDefault:!1,hasChanged:dt};Symbol.metadata??=Symbol("metadata"),ct.litPropertyMetadata??=new WeakMap;var S=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ne){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let i=Symbol(),a=this.getPropertyDescriptor(t,i,e);a!==void 0&&mo(this.prototype,t,a)}}static getPropertyDescriptor(t,e,i){let{get:a,set:r}=uo(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:a,set(n){let l=a?.call(this);r?.call(this,n),this.requestUpdate(t,l,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ne}static _$Ei(){if(this.hasOwnProperty(K("elementProperties")))return;let t=vo(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(K("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(K("properties"))){let e=this.properties,i=[...po(e),...fo(e)];for(let a of i)this.createProperty(a,e[a])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[i,a]of e)this.elementProperties.set(i,a)}this._$Eh=new Map;for(let[e,i]of this.elementProperties){let a=this._$Eu(e,i);a!==void 0&&this._$Eh.set(a,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let i=new Set(t.flat(1/0).reverse());for(let a of i)e.unshift(kt(a))}else t!==void 0&&e.push(kt(t));return e}static _$Eu(t,e){let i=e.attribute;return i===!1?void 0:typeof i=="string"?i:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ae(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){let i=this.constructor.elementProperties.get(t),a=this.constructor._$Eu(t,i);if(a!==void 0&&i.reflect===!0){let r=(i.converter?.toAttribute!==void 0?i.converter:G).toAttribute(e,i.type);this._$Em=t,r==null?this.removeAttribute(a):this.setAttribute(a,r),this._$Em=null}}_$AK(t,e){let i=this.constructor,a=i._$Eh.get(t);if(a!==void 0&&this._$Em!==a){let r=i.getPropertyOptions(a),n=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:G;this._$Em=a;let l=n.fromAttribute(e,r.type);this[a]=l??this._$Ej?.get(a)??l,this._$Em=null}}requestUpdate(t,e,i,a=!1,r){if(t!==void 0){let n=this.constructor;if(a===!1&&(r=this[t]),i??=n.getPropertyOptions(t),!((i.hasChanged??dt)(r,e)||i.useDefault&&i.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,i))))return;this.C(t,e,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:a,wrapped:r},n){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),r!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),a===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[a,r]of this._$Ep)this[a]=r;this._$Ep=void 0}let i=this.constructor.elementProperties;if(i.size>0)for(let[a,r]of i){let{wrapped:n}=r,l=this[a];n!==!0||this._$AL.has(a)||l===void 0||this.C(a,void 0,r,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(e)):this._$EM()}catch(i){throw t=!1,this._$EM(),i}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};S.elementStyles=[],S.shadowRootOptions={mode:"open"},S[K("elementProperties")]=new Map,S[K("finalized")]=new Map,wo?.({ReactiveElement:S}),(ct.reactiveElementVersions??=[]).push("2.1.2");var It=globalThis,se=o=>o,ht=It.trustedTypes,le=ht?ht.createPolicy("lit-html",{createHTML:o=>o}):void 0,Dt="$lit$",A=`lit$${Math.random().toFixed(9).slice(2)}$`,Pt="?"+A,bo=`<${Pt}>`,T=document,Z=()=>T.createComment(""),Q=o=>o===null||typeof o!="object"&&typeof o!="function",Tt=Array.isArray,pe=o=>Tt(o)||typeof o?.[Symbol.iterator]=="function",Ft=`[ 	
\f\r]`,J=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ce=/-->/g,de=/>/g,D=RegExp(`>|${Ft}(?:([^\\s"'>=/]+)(${Ft}*=${Ft}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),he=/'/g,me=/"/g,fe=/^(?:script|style|textarea|title)$/i,Rt=o=>(t,...e)=>({_$litType$:o,strings:t,values:e}),p=Rt(1),ve=Rt(2),ge=Rt(3),_=Symbol.for("lit-noChange"),m=Symbol.for("lit-nothing"),ue=new WeakMap,P=T.createTreeWalker(T,129);function we(o,t){if(!Tt(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return le!==void 0?le.createHTML(t):t}var be=(o,t)=>{let e=o.length-1,i=[],a,r=t===2?"<svg>":t===3?"<math>":"",n=J;for(let l=0;l<e;l++){let s=o[l],d,g,f=-1,z=0;for(;z<s.length&&(n.lastIndex=z,g=n.exec(s),g!==null);)z=n.lastIndex,n===J?g[1]==="!--"?n=ce:g[1]!==void 0?n=de:g[2]!==void 0?(fe.test(g[2])&&(a=RegExp("</"+g[2],"g")),n=D):g[3]!==void 0&&(n=D):n===D?g[0]===">"?(n=a??J,f=-1):g[1]===void 0?f=-2:(f=n.lastIndex-g[2].length,d=g[1],n=g[3]===void 0?D:g[3]==='"'?me:he):n===me||n===he?n=D:n===ce||n===de?n=J:(n=D,a=void 0);let M=n===D&&o[l+1].startsWith("/>")?" ":"";r+=n===J?s+bo:f>=0?(i.push(d),s.slice(0,f)+Dt+s.slice(f)+A+M):s+A+(f===-2?l:M)}return[we(o,r+(o[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),i]},tt=class o{constructor({strings:t,_$litType$:e},i){let a;this.parts=[];let r=0,n=0,l=t.length-1,s=this.parts,[d,g]=be(t,e);if(this.el=o.createElement(d,i),P.currentNode=this.el.content,e===2||e===3){let f=this.el.content.firstChild;f.replaceWith(...f.childNodes)}for(;(a=P.nextNode())!==null&&s.length<l;){if(a.nodeType===1){if(a.hasAttributes())for(let f of a.getAttributeNames())if(f.endsWith(Dt)){let z=g[n++],M=a.getAttribute(f).split(A),nt=/([.?@])?(.*)/.exec(z);s.push({type:1,index:r,name:nt[2],strings:M,ctor:nt[1]==="."?ut:nt[1]==="?"?pt:nt[1]==="@"?ft:B}),a.removeAttribute(f)}else f.startsWith(A)&&(s.push({type:6,index:r}),a.removeAttribute(f));if(fe.test(a.tagName)){let f=a.textContent.split(A),z=f.length-1;if(z>0){a.textContent=ht?ht.emptyScript:"";for(let M=0;M<z;M++)a.append(f[M],Z()),P.nextNode(),s.push({type:2,index:++r});a.append(f[z],Z())}}}else if(a.nodeType===8)if(a.data===Pt)s.push({type:2,index:r});else{let f=-1;for(;(f=a.data.indexOf(A,f+1))!==-1;)s.push({type:7,index:r}),f+=A.length-1}r++}}static createElement(t,e){let i=T.createElement("template");return i.innerHTML=t,i}};function R(o,t,e=o,i){if(t===_)return t;let a=i!==void 0?e._$Co?.[i]:e._$Cl,r=Q(t)?void 0:t._$litDirective$;return a?.constructor!==r&&(a?._$AO?.(!1),r===void 0?a=void 0:(a=new r(o),a._$AT(o,e,i)),i!==void 0?(e._$Co??=[])[i]=a:e._$Cl=a),a!==void 0&&(t=R(o,a._$AS(o,t.values),a,i)),t}var mt=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:i}=this._$AD,a=(t?.creationScope??T).importNode(e,!0);P.currentNode=a;let r=P.nextNode(),n=0,l=0,s=i[0];for(;s!==void 0;){if(n===s.index){let d;s.type===2?d=new N(r,r.nextSibling,this,t):s.type===1?d=new s.ctor(r,s.name,s.strings,this,t):s.type===6&&(d=new vt(r,this,t)),this._$AV.push(d),s=i[++l]}n!==s?.index&&(r=P.nextNode(),n++)}return P.currentNode=T,a}p(t){let e=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},N=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,a){this.type=2,this._$AH=m,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=a,this._$Cv=a?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=R(this,t,e),Q(t)?t===m||t==null||t===""?(this._$AH!==m&&this._$AR(),this._$AH=m):t!==this._$AH&&t!==_&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):pe(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==m&&Q(this._$AH)?this._$AA.nextSibling.data=t:this.T(T.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:i}=t,a=typeof i=="number"?this._$AC(t):(i.el===void 0&&(i.el=tt.createElement(we(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===a)this._$AH.p(e);else{let r=new mt(a,this),n=r.u(this.options);r.p(e),this.T(n),this._$AH=r}}_$AC(t){let e=ue.get(t.strings);return e===void 0&&ue.set(t.strings,e=new tt(t)),e}k(t){Tt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,i,a=0;for(let r of t)a===e.length?e.push(i=new o(this.O(Z()),this.O(Z()),this,this.options)):i=e[a],i._$AI(r),a++;a<e.length&&(this._$AR(i&&i._$AB.nextSibling,a),e.length=a)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let i=se(t).nextSibling;se(t).remove(),t=i}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},B=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,a,r){this.type=1,this._$AH=m,this._$AN=void 0,this.element=t,this.name=e,this._$AM=a,this.options=r,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=m}_$AI(t,e=this,i,a){let r=this.strings,n=!1;if(r===void 0)t=R(this,t,e,0),n=!Q(t)||t!==this._$AH&&t!==_,n&&(this._$AH=t);else{let l=t,s,d;for(t=r[0],s=0;s<r.length-1;s++)d=R(this,l[i+s],e,s),d===_&&(d=this._$AH[s]),n||=!Q(d)||d!==this._$AH[s],d===m?t=m:t!==m&&(t+=(d??"")+r[s+1]),this._$AH[s]=d}n&&!a&&this.j(t)}j(t){t===m?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},ut=class extends B{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===m?void 0:t}},pt=class extends B{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==m)}},ft=class extends B{constructor(t,e,i,a,r){super(t,e,i,a,r),this.type=5}_$AI(t,e=this){if((t=R(this,t,e,0)??m)===_)return;let i=this._$AH,a=t===m&&i!==m||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,r=t!==m&&(i===m||a);a&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},vt=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){R(this,t)}},ye={M:Dt,P:A,A:Pt,C:1,L:be,R:mt,D:pe,V:R,I:N,H:B,N:pt,U:ft,B:ut,F:vt},yo=It.litHtmlPolyfillSupport;yo?.(tt,N),(It.litHtmlVersions??=[]).push("3.3.3");var Ce=(o,t,e)=>{let i=e?.renderBefore??t,a=i._$litPart$;if(a===void 0){let r=e?.renderBefore??null;i._$litPart$=a=new N(t.insertBefore(Z(),r),r,void 0,e??{})}return a._$AI(o),a};var Bt=globalThis,y=class extends S{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=Ce(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return _}};y._$litElement$=!0,y.finalized=!0,Bt.litElementHydrateSupport?.({LitElement:y});var Co=Bt.litElementPolyfillSupport;Co?.({LitElement:y});(Bt.litElementVersions??=[]).push("4.2.2");var xe={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},gt=o=>(...t)=>({_$litDirective$:o,values:t}),q=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};var{I:bi}=ye;var Le=(o,t)=>t===void 0?o?._$litType$!==void 0:o?._$litType$===t;var xo={},$e=(o,t=xo)=>o._$AH=t;var ze=gt(class extends q{constructor(){super(...arguments),this.key=m}render(o,t){return this.key=o,t}update(o,[t,e]){return t!==this.key&&($e(o),this.key=t),e}});var wt=class{constructor(t){this.onStatus=t;this.socket=null;this.connected=!1;this.nextId=0;this.pending=new Map}connect(t){this.disconnect(),this.onStatus("connecting");let e=new WebSocket(`ws://${location.host}/api/websocket`);this.socket=e,e.onopen=()=>{this.socket===e&&e.send(JSON.stringify({token:t}))},e.onmessage=i=>{if(this.socket!==e)return;let a=JSON.parse(i.data);if(a.type==="ready"){this.connected=!0,this.onStatus("connected");return}if(a.id===void 0)return;let r=this.pending.get(a.id);r&&(clearTimeout(r.timer),this.pending.delete(a.id),a.error?r.reject(new Error(a.error.message)):r.resolve(a.result))},e.onclose=i=>{if(this.socket===e){if(this.disconnect(),i.code===1008){this.onStatus("denied");return}this.reconnectTimer=setTimeout(()=>this.connect(t),2e3)}}}disconnect(){clearTimeout(this.reconnectTimer);let t=this.socket;this.socket=null,this.connected=!1,t?.close(),this.onStatus("disconnected");for(let e of this.pending.values())clearTimeout(e.timer),e.reject(new Error("Connection lost; please refresh the data."));this.pending.clear()}callWS(t,e){let i=this.socket;if(i?.readyState!==WebSocket.OPEN||!this.connected)return Promise.reject(new Error("Not connected."));let a=++this.nextId;return new Promise((r,n)=>{let l=setTimeout(()=>{this.pending.delete(a),n(new Error("Request timed out."))},65e3);this.pending.set(a,{resolve:s=>r(s),reject:n,timer:l}),i.send(JSON.stringify({id:a,type:t,...e}))})}};var Se=o=>o.callWS("devices/list",{}),Ae=o=>o.callWS("devices/discover",{}),_e=(o,t)=>o.callWS("devices/save",t),Ee=(o,t)=>o.callWS("device/health",{device:t}),Me=(o,t)=>o.callWS("device/apis",{device:t}),ke=(o,t)=>o.callWS("device/interfaces",{device:t}),Fe=(o,t,e)=>o.callWS("device/read",{device:t,name:e});var Lo=v`
  :root {
    color-scheme: light dark;
    --axis-color-background: light-dark(#f5f7fa, #11151c);
    --axis-color-surface: light-dark(#ffffff, #1d2430);
    --axis-color-surface-muted: light-dark(#eaf0f6, #293342);
    --axis-color-text: light-dark(#202630, #edf2f8);
    --axis-color-border: light-dark(#bac5d2, #58677b);
    --axis-color-primary: light-dark(#005e9e, #8bcbff);
    --axis-color-on-primary: light-dark(#ffffff, #072c48);
    --axis-color-danger: light-dark(#a00000, #ffb4ab);
    --axis-color-warning: light-dark(#805000, #ffd08a);
    --axis-font-family: system-ui, sans-serif;
    --axis-font-size: 1rem;
    --axis-font-weight-medium: 600;
    --axis-line-height: 1.5;
    --axis-space-1: 0.25rem;
    --axis-space-2: 0.5rem;
    --axis-space-3: 0.75rem;
    --axis-space-4: 1rem;
    --axis-space-6: 1.5rem;
    --axis-radius-control: 0.5rem;
    --axis-radius-card: 0.75rem;
    --axis-border-width: 1px;
    --axis-control-height: 2.75rem;
    --axis-content-width: 62.5rem;
    --axis-focus-ring: 2px solid var(--axis-color-primary);

    --wa-font-family-body: var(--axis-font-family);
    --wa-font-size-m: var(--axis-font-size);
    --wa-color-text-normal: var(--axis-color-text);
    --wa-color-surface-default: var(--axis-color-surface);
    --wa-color-surface-border: var(--axis-color-border);
    --wa-color-neutral-fill-loud: var(--axis-color-text);
    --wa-color-neutral-on-loud: var(--axis-color-surface);
    --wa-color-neutral-fill-normal: var(--axis-color-surface-muted);
    --wa-color-neutral-on-normal: var(--axis-color-text);
    --wa-color-neutral-fill-quiet: var(--axis-color-surface-muted);
    --wa-color-neutral-on-quiet: var(--axis-color-text);
    --wa-color-neutral-border-normal: var(--axis-color-border);
    --wa-color-neutral-border-quiet: var(--axis-color-border);
    --wa-color-neutral-border-loud: var(--axis-color-border);
    --wa-color-brand-fill-loud: var(--axis-color-primary);
    --wa-color-brand-on-loud: var(--axis-color-on-primary);
    --wa-color-brand-fill-normal: var(--axis-color-surface-muted);
    --wa-color-brand-on-normal: var(--axis-color-primary);
    --wa-color-brand-fill-quiet: var(--axis-color-surface-muted);
    --wa-color-brand-on-quiet: var(--axis-color-primary);
    --wa-color-brand-border-normal: var(--axis-color-primary);
    --wa-color-brand-border-quiet: var(--axis-color-border);
    --wa-color-brand-border-loud: var(--axis-color-primary);
    --wa-color-mix-hover: var(--axis-color-border) 20%;
    --wa-color-mix-active: var(--axis-color-border) 30%;
    --wa-focus-ring: var(--axis-focus-ring);
    --wa-focus-ring-offset: var(--axis-space-1);

    font-family: var(--axis-font-family);
    font-size: var(--axis-font-size);
    line-height: var(--axis-line-height);
    color: var(--axis-color-text);
    background: var(--axis-color-background);
  }

  body {
    margin: 0;
  }
`,Ie=document.createElement("style");Ie.textContent=Lo.cssText;document.head.append(Ie);var U=v`
  :host {
    display: block;
    min-inline-size: 0;
  }
  h2 {
    margin-block: 0 var(--axis-space-4);
    overflow-wrap: anywhere;
  }
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--axis-space-2);
    margin-block-start: var(--axis-space-2);
  }
  .warning {
    color: var(--axis-color-warning);
    font-weight: var(--axis-font-weight-medium);
  }
  dl {
    display: grid;
    grid-template-columns: max-content minmax(0, 1fr);
    gap: var(--axis-space-2) var(--axis-space-4);
  }
  dd {
    margin: 0;
    overflow-wrap: anywhere;
  }
  pre {
    overflow: auto;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    background: var(--axis-color-surface-muted);
    padding: var(--axis-space-4);
    border-radius: var(--axis-radius-control);
  }
`;var k=o=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(o,t)}):customElements.define(o,t)};var $o={attribute:!0,type:String,converter:G,reflect:!1,hasChanged:dt},zo=(o=$o,t,e)=>{let{kind:i,metadata:a}=e,r=globalThis.litPropertyMetadata.get(a);if(r===void 0&&globalThis.litPropertyMetadata.set(a,r=new Map),i==="setter"&&((o=Object.create(o)).wrapped=!0),r.set(e.name,o),i==="accessor"){let{name:n}=e;return{set(l){let s=t.get.call(this);t.set.call(this,l),this.requestUpdate(n,s,o,!0,l)},init(l){return l!==void 0&&this.C(n,void 0,o,l),l}}}if(i==="setter"){let{name:n}=e;return function(l){let s=this[n];t.call(this,l),this.requestUpdate(n,s,o,!0,l)}}throw Error("Unsupported decorator location: "+i)};function c(o){return(t,e)=>typeof e=="object"?zo(o,t,e):((i,a,r)=>{let n=a.hasOwnProperty(r);return a.constructor.createProperty(r,i),n?Object.getOwnPropertyDescriptor(a,r):void 0})(o,t,e)}function et(o){return c({...o,state:!0,attribute:!1})}var O=(o,t,e)=>(e.configurable=!0,e.enumerable=!0,Reflect.decorate&&typeof t!="object"&&Object.defineProperty(o,t,e),e);function Ot(o,t){return(e,i,a)=>{let r=n=>n.renderRoot?.querySelector(o)??null;if(t){let{get:n,set:l}=typeof i=="object"?e:a??(()=>{let s=Symbol();return{get(){return this[s]},set(d){this[s]=d}}})();return O(e,i,{get(){let s=n.call(this);return s===void 0&&(s=r(this),(s!==null||this.hasUpdated)&&l.call(this,s)),s}})}return O(e,i,{get(){return r(this)}})}}var ot=gt(class extends q{constructor(o){if(super(o),o.type!==xe.ATTRIBUTE||o.name!=="class"||o.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(o){return" "+Object.keys(o).filter(t=>o[t]).join(" ")+" "}update(o,[t]){if(this.st===void 0){this.st=new Set,o.strings!==void 0&&(this.nt=new Set(o.strings.join(" ").split(/\s/).filter(i=>i!=="")));for(let i in t)t[i]&&!this.nt?.has(i)&&this.st.add(i);return this.render(t)}let e=o.element.classList;for(let i of this.st)i in t||(e.remove(i),this.st.delete(i));for(let i in t){let a=!!t[i];a===this.st.has(i)||this.nt?.has(i)||(a?(e.add(i),this.st.add(i)):(e.remove(i),this.st.delete(i)))}return _}});var L=o=>o??m;var Pe=Symbol.for(""),So=o=>{if(o?.r===Pe)return o?._$litStatic$};var Nt=(o,...t)=>({_$litStatic$:t.reduce((e,i,a)=>e+(r=>{if(r._$litStatic$!==void 0)return r._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${r}. Use 'unsafeStatic' to pass non-literal values, but
            take care to ensure page security.`)})(i)+o[a+1],o[0]),r:Pe}),De=new Map,qt=o=>(t,...e)=>{let i=e.length,a,r,n=[],l=[],s,d=0,g=!1;for(;d<i;){for(s=t[d];d<i&&(r=e[d],(a=So(r))!==void 0);)s+=a+t[++d],g=!0;d!==i&&l.push(r),n.push(s),d++}if(d===i&&n.push(t[i]),g){let f=n.join("$$lit$$");(t=De.get(f))===void 0&&(n.raw=n,De.set(f,t=n)),e=l}return o(t,...e)},bt=qt(p),va=qt(ve),ga=qt(ge);var V=class extends Event{constructor(){super("wa-invalid",{bubbles:!0,cancelable:!1,composed:!0})}};var Te={small:"s",medium:"m",large:"l"};var Re=new Set;function Be(o,t){t in Te&&!Re.has(`${o}:${t}`)&&(Re.add(`${o}:${t}`),console.warn(`[${o}] size="${t}" is deprecated. Use size="${Te[t]}" instead. The long-form value will be removed in the next major version.`))}var H=class{constructor(t,...e){this.slotNames=[],this.handleSlotChange=i=>{let a=i.target;(this.slotNames.includes("[default]")&&!a.name||a.name&&this.slotNames.includes(a.name))&&this.host.requestUpdate()},(this.host=t).addController(this),this.slotNames=e}hasDefaultSlot(){return this.host.childNodes?[...this.host.childNodes].some(t=>{if(t.nodeType===Node.TEXT_NODE&&t.textContent.trim()!=="")return!0;if(t.nodeType===Node.ELEMENT_NODE){let e=t;if(e.tagName.toLowerCase()==="wa-visually-hidden")return!1;if(!e.hasAttribute("slot"))return!0}return!1}):!1}hasNamedSlot(t){return this.host.querySelector?.(`:scope > [slot="${t}"]`)!==null}test(t,e){return e&&this.host.didSSR&&!this.host.hasUpdated?!!this.host[e]:t==="[default]"?this.hasDefaultSlot():this.hasNamedSlot(t)}hostConnected(){let t=this.host.shadowRoot;t&&"addEventListener"in t&&t.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){let t=this.host.shadowRoot;t&&"removeEventListener"in t&&t.removeEventListener("slotchange",this.handleSlotChange)}};var Oe=()=>({checkValidity(o){let t=o.input,e={message:"",isValid:!0,invalidKeys:[]};if(!t)return e;let i=!0;if("checkValidity"in t&&(i=t.checkValidity()),i)return e;if(e.isValid=!1,"validationMessage"in t&&(e.message=t.validationMessage),!("validity"in t))return e.invalidKeys.push("customError"),e;for(let a in t.validity){if(a==="valid")continue;let r=a;t.validity[r]&&e.invalidKeys.push(r)}return e}});function F(o,t){let e={waitUntilFirstUpdate:!1,...t};return(i,a)=>{let{update:r}=i,n=Array.isArray(o)?o:[o];i.update=function(l){n.forEach(s=>{let d=s;if(l.has(d)){let g=l.get(d),f=this[d];g!==f&&(!e.waitUntilFirstUpdate||this.hasUpdated)&&this[a](g,f)}}),r.call(this,l)}}}var Ne=()=>({observedAttributes:["custom-error"],checkValidity(o){let t={message:"",isValid:!0,invalidKeys:[]};return o.customError&&(t.message=o.customError,t.isValid=!1,t.invalidKeys=["customError"]),t}});var qe=v`:host {
  box-sizing: border-box;
}
:host *,
:host *::before,
:host *::after {
  box-sizing: inherit;
}
[hidden],
:host([hidden]) {
  display: none !important;
}
`;var yt=class extends Set{constructor(t,e=null){super(),this._existing=null,this._el=t,this._existing=e}add(t){super.add(t);let e=this._existing;if(e)try{e.add(t)}catch{e.add(`--${t}`)}else this._el.setAttribute(`state-${t}`,"");return this}delete(t){super.delete(t);let e=this._existing;return e?(e.delete(t),e.delete(`--${t}`)):this._el.removeAttribute(`state-${t}`),!0}has(t){return super.has(t)}clear(){for(let t of this)this.delete(t)}};if(typeof CSSStyleSheet<"u"){let o=CSSStyleSheet.prototype.replaceSync;Object.defineProperty(CSSStyleSheet.prototype,"replaceSync",{value:function(t){t=t.replace(/:state\(([^)]+)\)/g,":is(:state($1), :--$1, [state-$1])"),o.call(this,t)}})}var Ao=Object.defineProperty,_o=Object.getOwnPropertyDescriptor,Ve=o=>{throw TypeError(o)},Ut=(o,t,e,i)=>{for(var a=i>1?void 0:i?_o(t,e):t,r=o.length-1,n;r>=0;r--)(n=o[r])&&(a=(i?n(t,e,a):n(a))||a);return i&&a&&Ao(t,e,a),a},He=(o,t,e)=>t.has(o)||Ve("Cannot "+e),Eo=(o,t,e)=>(He(o,t,"read from private field"),e?e.call(o):t.get(o)),Mo=(o,t,e)=>t.has(o)?Ve("Cannot add the same private member more than once"):t instanceof WeakSet?t.add(o):t.set(o,e),ko=(o,t,e,i)=>(He(o,t,"write to private field"),i?i.call(o,e):t.set(o,e),e),Fo=/;\s+$/;function Io(o){return o.replace(/[A-Z]/g,t=>`-${t.toLowerCase()}`)}function Ue(o){let{property:t,value:e,element:i}=o;if(e){let a=i.getAttribute("style")||"";a&&(a.match(Fo)||(a+=";"),a+=" ");let r=`${t}: ${e}`;return a.includes(r)?void 0:`${a}${r};`}return null}var Ct,x=class extends y{constructor(){super(),Mo(this,Ct,!1),this.initialReflectedProperties=new Map,this.didSSR=!!this.shadowRoot,this.customStates={set:(e,i)=>{if(this.internals?.states)try{i?this.internals.states.add(e):this.internals.states.delete(e)}catch(a){if(String(a).includes("must start with '--'"))console.error("Your browser implements an outdated version of CustomStateSet. Consider using a polyfill");else throw a}},has:e=>{if(!this.internals?.states)return!1;try{return this.internals.states.has(e)}catch{return!1}}};try{this.internals=this.attachInternals()}catch{console.error("Element internals are not supported in your browser. Consider using a polyfill")}this.customStates.set("wa-defined",!0);let t=this.constructor;for(let[e,i]of t.elementProperties)i.default==="inherit"&&i.initial!==void 0&&typeof e=="string"&&this.customStates.set(`initial-${e}-${i.initial}`,!0)}static get styles(){let t=Array.isArray(this.css)?this.css:this.css?[this.css]:[];return[qe,...t]}attachInternals(){let t=super.attachInternals();return Object.defineProperty(t,"states",{value:new yt(this,t.states)}),t}connectedCallback(){super.connectedCallback(),this.didSSR||this.shadowRoot?.prepend(document.createComment(` Web Awesome: https://webawesome.com/docs/components/${this.localName.replace("wa-","")} `)),this.didSSR&&this.updateComplete.then(()=>{this.shadowRoot?.prepend(document.createComment(` Web Awesome: https://webawesome.com/docs/components/${this.localName.replace("wa-","")} `))})}attributeChangedCallback(t,e,i){Eo(this,Ct)||(this.constructor.elementProperties.forEach((a,r)=>{a.reflect&&this[r]!=null&&this.initialReflectedProperties.set(r,this[r])}),ko(this,Ct,!0)),super.attributeChangedCallback(t,e,i)}willUpdate(t){super.willUpdate(t),this.initialReflectedProperties.forEach((e,i)=>{t.has(i)&&this[i]==null&&(this[i]=e)})}firstUpdated(t){super.firstUpdated(t),this.didSSR&&this.shadowRoot?.querySelectorAll("slot").forEach(e=>{e.dispatchEvent(new Event("slotchange",{bubbles:!0,composed:!1,cancelable:!1}))})}update(t){try{super.update(t)}catch(e){if(this.didSSR&&!this.hasUpdated){let i=new Event("lit-hydration-error",{bubbles:!0,composed:!0,cancelable:!1});i.error=e,this.dispatchEvent(i)}throw e}}setStyle(t,e){if(!this.style){let i=Ue({property:Io(t),value:e,element:this});i&&this.setAttribute("style",i);return}this.style[t]=e}setStyleProperty(t,e){if(!this.style){let i=Ue({property:t,value:e,element:this});i&&this.setAttribute("style",i);return}this.style.setProperty(t,e)}relayNativeEvent(t,e){t.stopImmediatePropagation(),this.dispatchEvent(new t.constructor(t.type,{...t,...e}))}};Ct=new WeakMap;Ut([c()],x.prototype,"dir",2);Ut([c()],x.prototype,"lang",2);Ut([c({type:Boolean,reflect:!0,attribute:"did-ssr"})],x.prototype,"didSSR",2);var Do=Object.defineProperty,Po=Object.getOwnPropertyDescriptor,j=(o,t,e,i)=>{for(var a=i>1?void 0:i?Po(t,e):t,r=o.length-1,n;r>=0;r--)(n=o[r])&&(a=(i?n(t,e,a):n(a))||a);return i&&a&&Do(t,e,a),a},$=class extends x{constructor(){super(),this.name=null,this.disabled=!1,this.required=!1,this.assumeInteractionOn=["input"],this.validators=[],this.valueHasChanged=!1,this.hasInteracted=!1,this.customError=null,this.emittedEvents=[],this.emitInvalid=t=>{t.target===this&&(this.hasInteracted=!0,this.dispatchEvent(new V))},this.handleInteraction=t=>{let e=this.emittedEvents;e.includes(t.type)||e.push(t.type),e.length===this.assumeInteractionOn?.length&&(this.hasInteracted=!0)},"addEventListener"in this&&this.addEventListener("invalid",this.emitInvalid)}static get validators(){return[Ne()]}static get observedAttributes(){let t=new Set(super.observedAttributes||[]);for(let e of this.validators)if(e.observedAttributes)for(let i of e.observedAttributes)t.add(i);return[...t]}connectedCallback(){super.connectedCallback(),this.didSSR&&!this.hasUpdated?this.updateComplete.then(()=>{this.updateValidity()}):this.updateValidity(),this.assumeInteractionOn.forEach(t=>{this.addEventListener?.(t,this.handleInteraction)})}firstUpdated(...t){super.firstUpdated(...t),this.updateValidity()}willUpdate(t){if(!!1&&t.has("customError")&&(this.customError||(this.customError=null),this.setCustomValidity(this.customError||"")),t.has("value")||t.has("disabled")||t.has("defaultValue")){let e=this.value;this.updateFormValue(e)}t.has("disabled")&&(this.customStates.set("disabled",this.disabled),(this.hasAttribute("disabled")||!!1&&!this.matches(":disabled"))&&this.toggleAttribute("disabled",this.disabled)),super.willUpdate(t),this.didSSR&&!this.hasUpdated?this.updateComplete.then(()=>this.updateValidity()):this.updateValidity()}updateFormValue(t){if(Array.isArray(t)){if(this.name){let e=new FormData;for(let i of t)e.append(this.name,i);this.setValue(e,e)}}else this.setValue(t,t)}get labels(){return this.internals.labels}getForm(){return this.internals.form}set form(t){t?this.setAttribute("form",t):this.removeAttribute("form")}get form(){return this.internals.form}get validity(){return this.internals.validity}get willValidate(){return this.internals.willValidate}get validationMessage(){return this.internals.validationMessage}checkValidity(){return this.updateValidity(),this.internals.checkValidity()}reportValidity(){return this.updateValidity(),this.hasInteracted=!0,this.internals.reportValidity()}get validationTarget(){return this.input||void 0}setValidity(...t){let e=t[0],i=t[1],a=t[2];a||(a=this.validationTarget),this.internals.setValidity(e,i,a||void 0),this.requestUpdate("validity"),this.setCustomStates()}setCustomStates(){let t=!!this.required,e=this.internals.validity.valid,i=this.hasInteracted;this.customStates.set("required",t),this.customStates.set("optional",!t),this.customStates.set("invalid",!e),this.customStates.set("valid",e),this.customStates.set("user-invalid",!e&&i),this.customStates.set("user-valid",e&&i)}setCustomValidity(t){if(!t){this.customError=null,this.setValidity({});return}this.customError=t,this.setValidity({customError:!0},t,this.validationTarget)}formResetCallback(){this.resetValidity(),this.hasInteracted=!1,this.valueHasChanged=!1,this.emittedEvents=[],this.updateValidity()}formDisabledCallback(t){this.disabled=t,this.updateValidity()}formStateRestoreCallback(t,e){this.didSSR&&!this.hasUpdated?this.updateComplete.then(()=>{this.value=t,e==="restore"&&this.resetValidity(),this.updateValidity()}):(this.value=t,e==="restore"&&this.resetValidity(),this.updateValidity())}setValue(...t){let[e,i]=t;this.internals.setFormValue(e,i)}get allValidators(){let t=this.constructor.validators||[],e=this.validators||[];return[...t,...e]}resetValidity(){this.setCustomValidity(""),this.setValidity({})}updateValidity(){if(this.disabled||this.hasAttribute("disabled")||!this.willValidate){this.resetValidity();return}let t=this.allValidators;if(!t?.length)return;let e={customError:!!this.customError},i=this.validationTarget||this.input||void 0,a="";for(let r of t){let{isValid:n,message:l,invalidKeys:s}=r.checkValidity(this);n||(a||(a=l),s?.length>=0&&s.forEach(d=>e[d]=!0))}a||(a=this.validationMessage),this.setValidity(e,a,i)}};$.formAssociated=!0;j([c({reflect:!0})],$.prototype,"name",2);j([c({type:Boolean})],$.prototype,"disabled",2);j([c({state:!0,attribute:!1})],$.prototype,"valueHasChanged",2);j([c({state:!0,attribute:!1})],$.prototype,"hasInteracted",2);j([c({attribute:"custom-error",reflect:!0})],$.prototype,"customError",2);j([c({attribute:!1,state:!0,type:Object})],$.prototype,"validity",1);var xt=v`:host([size="xs"]) {
  font-size: var(--wa-font-size-xs);
}
:host([size="s"]),
:host([size="small"]) {
  font-size: var(--wa-font-size-s);
}
:host([size="m"]),
:host([size="medium"]) {
  font-size: var(--wa-font-size-m);
}
:host([size="l"]),
:host([size="large"]) {
  font-size: var(--wa-font-size-l);
}
:host([size="xl"]) {
  font-size: var(--wa-font-size-xl);
}
`;var je=v`:where(:root),
.wa-neutral,
:host([variant="neutral"]) {
  --wa-color-fill-loud: var(--wa-color-neutral-fill-loud);
  --wa-color-fill-normal: var(--wa-color-neutral-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-neutral-fill-quiet);
  --wa-color-border-loud: var(--wa-color-neutral-border-loud);
  --wa-color-border-normal: var(--wa-color-neutral-border-normal);
  --wa-color-border-quiet: var(--wa-color-neutral-border-quiet);
  --wa-color-on-loud: var(--wa-color-neutral-on-loud);
  --wa-color-on-normal: var(--wa-color-neutral-on-normal);
  --wa-color-on-quiet: var(--wa-color-neutral-on-quiet);
}
.wa-brand,
:host([variant="brand"]) {
  --wa-color-fill-loud: var(--wa-color-brand-fill-loud);
  --wa-color-fill-normal: var(--wa-color-brand-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-brand-fill-quiet);
  --wa-color-border-loud: var(--wa-color-brand-border-loud);
  --wa-color-border-normal: var(--wa-color-brand-border-normal);
  --wa-color-border-quiet: var(--wa-color-brand-border-quiet);
  --wa-color-on-loud: var(--wa-color-brand-on-loud);
  --wa-color-on-normal: var(--wa-color-brand-on-normal);
  --wa-color-on-quiet: var(--wa-color-brand-on-quiet);
}
.wa-success,
:host([variant="success"]) {
  --wa-color-fill-loud: var(--wa-color-success-fill-loud);
  --wa-color-fill-normal: var(--wa-color-success-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-success-fill-quiet);
  --wa-color-border-loud: var(--wa-color-success-border-loud);
  --wa-color-border-normal: var(--wa-color-success-border-normal);
  --wa-color-border-quiet: var(--wa-color-success-border-quiet);
  --wa-color-on-loud: var(--wa-color-success-on-loud);
  --wa-color-on-normal: var(--wa-color-success-on-normal);
  --wa-color-on-quiet: var(--wa-color-success-on-quiet);
}
.wa-warning,
:host([variant="warning"]) {
  --wa-color-fill-loud: var(--wa-color-warning-fill-loud);
  --wa-color-fill-normal: var(--wa-color-warning-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-warning-fill-quiet);
  --wa-color-border-loud: var(--wa-color-warning-border-loud);
  --wa-color-border-normal: var(--wa-color-warning-border-normal);
  --wa-color-border-quiet: var(--wa-color-warning-border-quiet);
  --wa-color-on-loud: var(--wa-color-warning-on-loud);
  --wa-color-on-normal: var(--wa-color-warning-on-normal);
  --wa-color-on-quiet: var(--wa-color-warning-on-quiet);
}
.wa-danger,
:host([variant="danger"]) {
  --wa-color-fill-loud: var(--wa-color-danger-fill-loud);
  --wa-color-fill-normal: var(--wa-color-danger-fill-normal);
  --wa-color-fill-quiet: var(--wa-color-danger-fill-quiet);
  --wa-color-border-loud: var(--wa-color-danger-border-loud);
  --wa-color-border-normal: var(--wa-color-danger-border-normal);
  --wa-color-border-quiet: var(--wa-color-danger-border-quiet);
  --wa-color-on-loud: var(--wa-color-danger-on-loud);
  --wa-color-on-normal: var(--wa-color-danger-on-normal);
  --wa-color-on-quiet: var(--wa-color-danger-on-quiet);
}
`;var Vt=new Set,W=new Map,E,Ht="ltr",jt="en",We=typeof MutationObserver<"u"&&typeof document<"u"&&typeof document.documentElement<"u";if(We){let o=new MutationObserver(Xe);Ht=document.documentElement.dir||"ltr",jt=document.documentElement.lang||navigator.language,o.observe(document.documentElement,{attributes:!0,attributeFilter:["dir","lang"]})}function at(...o){o.map(t=>{let e=t.$code.toLowerCase();W.has(e)?W.set(e,Object.assign(Object.assign({},W.get(e)),t)):W.set(e,t),E||(E=t)}),Xe()}function Xe(){We&&(Ht=document.documentElement.dir||"ltr",jt=document.documentElement.lang||navigator.language),[...Vt.keys()].map(o=>{typeof o.requestUpdate=="function"&&o.requestUpdate()})}var Lt=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){Vt.add(this.host)}hostDisconnected(){Vt.delete(this.host)}dir(){return`${this.host.dir||Ht}`.toLowerCase()}lang(){let t=`${this.host.lang||jt}`.toLowerCase().replace(/_/g,"-");try{return new Intl.Locale(t),t}catch{return E?E.$code.toLowerCase():"en"}}getTranslationData(t){var e,i;let a;try{a=new Intl.Locale(t.replace(/_/g,"-"))}catch{return{locale:void 0,language:"",region:"",primary:void 0,secondary:void 0}}let r=a.language.toLowerCase(),n=(i=(e=a.region)===null||e===void 0?void 0:e.toLowerCase())!==null&&i!==void 0?i:"",l=W.get(`${r}-${n}`),s=W.get(r);return{locale:a,language:r,region:n,primary:l,secondary:s}}exists(t,e){var i;let{primary:a,secondary:r}=this.getTranslationData((i=e.lang)!==null&&i!==void 0?i:this.lang());return e=Object.assign({includeFallback:!1},e),!!(a&&a[t]||r&&r[t]||e.includeFallback&&E&&E[t])}term(t,...e){let{primary:i,secondary:a}=this.getTranslationData(this.lang()),r;if(i&&i[t])r=i[t];else if(a&&a[t])r=a[t];else if(E&&E[t])r=E[t];else return console.error(`No translation found for: ${String(t)}`),String(t);return typeof r=="function"?r(...e):r}date(t,e){return t=new Date(t),new Intl.DateTimeFormat(this.lang(),e).format(t)}number(t,e){return t=Number(t),isNaN(t)?"":new Intl.NumberFormat(this.lang(),e).format(t)}relativeTime(t,e,i){return new Intl.RelativeTimeFormat(this.lang(),i).format(t,e)}};var Ye={$code:"en",$name:"English",$dir:"ltr",allTagsRemoved:"All tags removed",am:"AM",autosizeColumn:"Autosize column",captions:"Captions",carousel:"Carousel",chooseDate:"Choose date",chooseDecade:"Choose decade",chooseMonth:"Choose month",chooseTime:"Choose time",chooseYear:"Choose year",clearEntry:"Clear entry",clearFilter:"Clear filter",clearSort:"Clear sort",close:"Close",closeCalendar:"Close calendar",closeTimeInput:"Close time picker",collapseRow:"Collapse row",columnMenu:"Column options",columnMovedToPosition:(o,t,e)=>`${o} moved to position ${t} of ${e}`,columns:"Columns",compactPageXOfY:(o,t)=>`${o} of ${t}`,completed:"Completed",copied:"Copied",copy:"Copy",createOption:o=>`Create "${o}"`,currentlyPlaying:"currently playing",currentValue:"Current value",date:"Date",datePickerKeyboardHelp:"Use arrow keys to change values; press Alt+Down Arrow to open the calendar.",day:"Day",dayPeriod:"AM/PM",decrement:"Decrement",deselectAllRows:"Deselect all rows",disabled:"Disabled",dropFileHere:"Drop file here or click to browse",dropFilesHere:"Drop files here or click to browse",empty:"Empty",endDate:"End date",enterFullscreen:"Enter fullscreen",error:"Error",exitFullscreen:"Exit fullscreen",expandRow:"Expand row",filterByColumn:o=>`Filter by ${o}`,filterFrom:"From",filterMax:"Max",filterMin:"Min",filterTo:"To",firstPage:"First page",goToSlide:(o,t)=>`Go to slide ${o} of ${t}`,hideColumn:"Hide column",hidePassword:"Hide password",hour:"Hour",incompleteDate:"Enter a valid date.",increment:"Increment",jumpBackwardX:o=>`Jump back ${o} pages`,jumpForwardX:o=>`Jump forward ${o} pages`,lastPage:"Last page",loading:"Loading",locked:"Locked",minute:"Minute",month:"Month",moreOptions:"More Options",mute:"Mute",nextDecade:"Next decade",nextMonth:"Next month",nextPage:"Next page",nextSlide:"Next slide",nextVideo:"Next Video",nextYear:"Next year",noData:"No data",noOptions:"No options",noResults:"No matching results",notCompleted:"Not completed",now:"Now",numCharacters:o=>o===1?"1 character":`${o} characters`,numCharactersRemaining:o=>o===1?"1 character remaining":`${o} characters remaining`,numOptionsAvailable:o=>o===0?"No options available":o===1?"1 option available":`${o} options available`,numOptionsSelected:o=>o===0?"No options selected":o===1?"1 option selected":`${o} options selected`,numRowsCopied:o=>o===1?"1 row copied":`${o} rows copied`,numRowsSelected:o=>o===1?"1 row selected":`${o} rows selected`,optionPosition:(o,t,e)=>`${o}, ${t} of ${e}`,optionsLoadError:"Options could not be loaded",pageXOfY:(o,t)=>`Page ${o} of ${t}`,pagination:"Pagination",pause:"Pause",pauseAnimation:"Pause animation",pictureInPicture:"Picture in picture",pinLeft:"Pin left",pinRight:"Pin right",play:"Play",playAnimation:"Play animation",playbackSpeed:"Playback speed",playlist:"Playlist",pm:"PM",previousDecade:"Previous decade",previousMonth:"Previous month",previousPage:"Previous page",previousSlide:"Previous slide",previousVideo:"Previous video",previousYear:"Previous year",progress:"Progress",rangeTooLong:o=>o===1?"Select a range no longer than 1 day":`Select a range no longer than ${o} days`,rangeTooShort:o=>o===1?"Select a range at least 1 day long":`Select a range at least ${o} days long`,readonly:"Read-only",remove:"Remove",resetColumns:"Reset columns",resize:"Resize",resizeColumn:"Resize column",rowsPerPage:"Rows per page",scrollableRegion:"Scrollable region",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",search:"Search",second:"Second",seek:"Seek",seekProgress:(o,t)=>`${o} of ${t}`,selectAColorFromTheScreen:"Select a color from the screen",selectAllRows:"Select all rows",selected:"Selected",selectedDateLabel:o=>`Selected: ${o}`,selectedRangeLabel:o=>`Selected range: ${o}`,selectGroup:"Select group",selectionCleared:"Selection cleared",selectRow:"Select row",showingNofMRows:(o,t)=>`Showing ${o} of ${t} rows`,showingXtoYofZ:(o,t,e)=>`${o}\u2013${t} of ${e}`,showPassword:"Show password",slideNum:o=>`Slide ${o}`,sortAscending:"Sort ascending",sortColumn:"Sort column",sortDescending:"Sort descending",startDate:"Start date",steps:"Steps",stepXOfY:(o,t)=>`Step ${o} of ${t}`,tagAdded:o=>`${o} added`,tagAlreadyAdded:o=>`${o} is already added`,tagInputKeyboardHelp:"Press Backspace or Delete to remove this tag.",tagRemoved:o=>`${o} removed`,time:"Time",timeInputKeyboardHelp:"Use arrow keys to change values; press Alt+Down Arrow to open the time picker.",today:"Today",toggleColorFormat:"Toggle color format",tooFewTags:o=>o===1?"Add at least 1 tag":`Add at least ${o} tags`,tooManyTags:o=>o===1?"Add no more than 1 tag":`Add no more than ${o} tags`,unmute:"Unmute",unpin:"Unpin",unpinColumn:"Unpin column",videoPlayer:"Video player",volume:"Volume",year:"Year",zoomIn:"Zoom in",zoomOut:"Zoom out"};at(Ye);var Ke=Ye;var X=class extends Lt{lang(){return this.host.didSSR&&!this.host.hasUpdated?this.host.lang||"en":super.lang()}};at(Ke);var $t=class extends Event{constructor(){super("wa-error",{bubbles:!0,cancelable:!1,composed:!0})}};var zt=class extends Event{constructor(){super("wa-load",{bubbles:!0,cancelable:!1,composed:!0})}};var Ge=v`:host {
  --primary-color: currentColor;
  --primary-opacity: 1;
  --secondary-color: currentColor;
  --secondary-opacity: 0.4;
  --rotate-angle: 0deg;
  box-sizing: content-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: -0.125em;
}
:host(:not([canvas])),
:host([canvas="fixed"]) {
  width: 1.25em;
  height: 1em;
  min-width: 1.25em;
  min-height: 1em;
}
:host([canvas="auto"]),
:host([auto-width]:not([canvas])) {
  width: auto;
  height: 1em;
}
:host([canvas="square"]) {
  width: 1.25em;
  height: 1.25em;
  min-width: 1.25em;
  min-height: 1.25em;
}
:host([canvas="roomy"]) {
  width: 1.5em;
  height: 1.5em;
  min-width: 1.5em;
  min-height: 1.5em;
}
svg {
  height: 1em;
  overflow: visible;
  width: auto;
}
svg path[data-duotone-primary] {
  color: var(--primary-color);
  opacity: var(--path-opacity, var(--primary-opacity));
}
svg path[data-duotone-secondary] {
  color: var(--secondary-color);
  opacity: var(--path-opacity, var(--secondary-opacity));
}
:host([rotate]) {
  transform: rotate(var(--rotate-angle, 0deg));
}
:host([flip="x"]) {
  transform: scaleX(-1);
}
:host([flip="y"]) {
  transform: scaleY(-1);
}
:host([flip="both"]) {
  transform: scale(-1, -1);
}
:host([rotate][flip="x"]) {
  transform: rotate(var(--rotate-angle, 0deg)) scaleX(-1);
}
:host([rotate][flip="y"]) {
  transform: rotate(var(--rotate-angle, 0deg)) scaleY(-1);
}
:host([rotate][flip="both"]) {
  transform: rotate(var(--rotate-angle, 0deg)) scale(-1, -1);
}
:host([animation="beat"]) {
  animation-name: beat;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="bounce"]) {
  animation-name: bounce;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, cubic-bezier(0.28, 0.84, 0.42, 1));
}
:host([animation="fade"]) {
  animation-name: fade;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="beat-fade"]) {
  animation-name: beat-fade;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="flip"]) {
  animation-name: flip;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1.5s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="flip-360"]) {
  animation-name: flip-360;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="shake"]) {
  animation-name: shake;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 0.75s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
}
:host([animation="spin"]) {
  animation-name: spin;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 2s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="spin-pulse"]) {
  animation-name: spin;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, steps(8));
}
:host([animation="spin-reverse"]) {
  animation-name: spin;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, reverse);
  animation-duration: var(--animation-duration, 2s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="spin-snap"]) {
  animation-name: spin-snap;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 3s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="spin-snap-4"]) {
  animation-name: spin-snap-4;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 2.4s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="spin-snap-8"]) {
  animation-name: spin-snap-8;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 4s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="buzz"]) {
  animation-name: buzz;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 0.6s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, linear);
}
:host([animation="wag"]) {
  animation-name: wag;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 0.9s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-out);
  transform-origin: bottom center;
}
:host([animation="float"]) {
  animation-name: float;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 3s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-in-out);
  will-change: transform;
}
:host([animation="swing"]) {
  animation-name: swing;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 1.2s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-out);
  transform-origin: top center;
}
:host([animation="jello"]) {
  animation-name: jello;
  animation-delay: var(--animation-delay, 0s);
  animation-direction: var(--animation-direction, normal);
  animation-duration: var(--animation-duration, 0.9s);
  animation-iteration-count: var(--animation-iteration-count, infinite);
  animation-timing-function: var(--animation-timing, ease-out);
}
@media (prefers-reduced-motion: reduce) {
  :host([animation="beat"]),
  :host([animation="bounce"]),
  :host([animation="fade"]),
  :host([animation="beat-fade"]),
  :host([animation="flip"]),
  :host([animation="flip-360"]),
  :host([animation="shake"]),
  :host([animation="spin"]),
  :host([animation="spin-pulse"]),
  :host([animation="spin-reverse"]),
  :host([animation="spin-snap"]),
  :host([animation="spin-snap-4"]),
  :host([animation="spin-snap-8"]),
  :host([animation="buzz"]),
  :host([animation="wag"]),
  :host([animation="float"]),
  :host([animation="swing"]),
  :host([animation="jello"]) {
    animation: none !important;
    transition: none !important;
  }
}
@keyframes beat {
  0% {
    transform: scale(1);
  }
  25% {
    transform: scale(calc(1.25 * var(--beat-scale, 1.25)));
  }
  45% {
    transform: scale(calc(1.22 * var(--beat-scale, 1.22)));
  }
  65% {
    transform: scale(calc(1.25 * var(--beat-scale, 1.25)));
  }
  90% {
    transform: scale(1);
  }
}
@keyframes bounce {
  0% {
    transform: scale(1, 1) translateY(0);
    animation-timing-function: var(--animation-timing);
  }
  14% {
    transform: scale(var(--bounce-start-scale-x, 1.06), var(--bounce-start-scale-y, 0.94)) translateY(var(--bounce-anticipation, 3px));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  32% {
    transform: scale(var(--bounce-jump-scale-x, 0.94), var(--bounce-jump-scale-y, 1.12)) translateY(calc(-1 * var(--bounce-height, 0.5em)));
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  52% {
    transform: scale(1, 1) translateY(calc(-1 * var(--bounce-height, 0.5em) * 1.1));
    animation-timing-function: cubic-bezier(0.5, 0, 1, 0.5);
  }
  70% {
    transform: scale(var(--bounce-land-scale-x, 1.06), var(--bounce-land-scale-y, 0.92)) translateY(0);
    animation-timing-function: cubic-bezier(0.33, 0.33, 0.66, 1);
  }
  85% {
    transform: scale(0.98, 1.04) translateY(calc(-2px * var(--bounce-rebound, 1)));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: scale(1, 1) translateY(0);
  }
}
@keyframes fade {
  0% {
    opacity: 1;
    transform: scale(1);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  40% {
    opacity: var(--fade-opacity, 0.4);
    transform: scale(0.98);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
@keyframes beat-fade {
  0% {
    opacity: var(--beat-fade-opacity, 0.4);
    transform: scale(1);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  25% {
    opacity: calc(var(--beat-fade-opacity, 0.4) + 0.4);
    transform: scale(var(--beat-fade-scale, 1.28));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  45% {
    opacity: 1;
    transform: scale(var(--beat-fade-scale, 1.25));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  65% {
    opacity: calc(var(--beat-fade-opacity, 0.4) + 0.4);
    transform: scale(var(--beat-fade-scale, 1.28));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  100% {
    opacity: var(--beat-fade-opacity, 0.4);
    transform: scale(1);
  }
}
@keyframes flip {
  0% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  8% {
    transform: perspective(2em) scale(var(--flip-anticipation-scale, 0.95)) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  35% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * 0.6));
    animation-timing-function: linear;
  }
  65% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * 0.5));
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  92% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * var(--flip-overshoot, 1.04)));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), var(--flip-angle, -360deg));
  }
}
@keyframes flip-360 {
  0% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.4, 1);
  }
  8% {
    transform: perspective(2em) scale(var(--flip-anticipation-scale, 0.95)) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), 0deg);
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  50% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * 0.6));
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  80% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), calc(var(--flip-angle, -360deg) * var(--flip-overshoot, 1.04)));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: perspective(2em) scale(1) rotate3d(var(--flip-x, 0), var(--flip-y, 1), var(--flip-z, 0), var(--flip-angle, -360deg));
  }
}
@keyframes shake {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.8, 1);
  }
  8% {
    transform: rotate(35deg) translateX(1px);
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  20% {
    transform: rotate(-22deg) translateX(-1px);
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  35% {
    transform: rotate(15deg) translateX(1px);
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  50% {
    transform: rotate(-9deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  65% {
    transform: rotate(5deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  78% {
    transform: rotate(-3deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  90% {
    transform: rotate(1deg);
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  100% {
    transform: rotate(0deg);
  }
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes spin-snap {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  12% {
    transform: rotate(60deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  16.67% {
    transform: rotate(60deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  28.67% {
    transform: rotate(120deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  33.33% {
    transform: rotate(120deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  45.33% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  62% {
    transform: rotate(240deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  66.67% {
    transform: rotate(240deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  78.67% {
    transform: rotate(300deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  83.33% {
    transform: rotate(300deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  95.33% {
    transform: rotate(360deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes spin-snap-4 {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  15% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  25% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  40% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  65% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  75% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  90% {
    transform: rotate(360deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes spin-snap-8 {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  9% {
    transform: rotate(45deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  12.5% {
    transform: rotate(45deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  21.5% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  25% {
    transform: rotate(90deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  34% {
    transform: rotate(135deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  37.5% {
    transform: rotate(135deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  46.5% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  59% {
    transform: rotate(225deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  62.5% {
    transform: rotate(225deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  71.5% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  75% {
    transform: rotate(270deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  84% {
    transform: rotate(315deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  87.5% {
    transform: rotate(315deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
  96.5% {
    transform: rotate(360deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes buzz {
  0% {
    transform: translateX(0) rotate(0deg);
    animation-timing-function: cubic-bezier(0.1, 0, 0.9, 1);
  }
  5% {
    transform: translateX(var(--buzz-distance, 4px)) rotate(0.5deg);
  }
  10% {
    transform: translateX(calc(-1 * var(--buzz-distance, 4px))) rotate(-0.5deg);
  }
  15% {
    transform: translateX(var(--buzz-distance, 4px)) rotate(0.3deg);
  }
  20% {
    transform: translateX(calc(-1 * var(--buzz-distance, 4px))) rotate(-0.3deg);
  }
  25% {
    transform: translateX(calc(var(--buzz-distance, 4px) * 0.7)) rotate(0.2deg);
  }
  30% {
    transform: translateX(calc(-1 * var(--buzz-distance, 4px) * 0.7)) rotate(-0.2deg);
  }
  35% {
    transform: translateX(calc(var(--buzz-distance, 4px) * 0.4)) rotate(0.1deg);
  }
  40% {
    transform: translateX(0) rotate(0deg);
  }
  100% {
    transform: translateX(0) rotate(0deg);
  }
}
@keyframes wag {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.6, 1);
  }
  12% {
    transform: rotate(var(--wag-angle, 12deg));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  24% {
    transform: rotate(2deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.6, 1);
  }
  36% {
    transform: rotate(calc(var(--wag-angle, 12deg) * 0.85));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  48% {
    transform: rotate(1deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.6, 1);
  }
  58% {
    transform: rotate(calc(var(--wag-angle, 12deg) * 0.6));
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  68% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(0deg);
  }
}
@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg) scale(var(--float-squash-x, 1.02), var(--float-squash-y, 0.98));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  15% {
    transform: translateY(calc(-0.4 * var(--float-height, 6px))) translateX(var(--float-drift, 1px)) rotate(var(--float-tilt, 1deg)) scale(1, 1);
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  35% {
    transform: translateY(calc(-1 * var(--float-height, 6px))) translateX(0) rotate(0deg) scale(var(--float-stretch-x, 0.98), var(--float-stretch-y, 1.03));
    animation-timing-function: cubic-bezier(0.5, 0, 0.5, 0);
  }
  50% {
    transform: translateY(calc(-0.92 * var(--float-height, 6px))) translateX(calc(-0.5 * var(--float-drift, 1px))) rotate(calc(-0.5 * var(--float-tilt, 1deg))) scale(0.995, 1.01);
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 0.33);
  }
  70% {
    transform: translateY(calc(-0.3 * var(--float-height, 6px))) translateX(calc(-1 * var(--float-drift, 1px))) rotate(calc(-1 * var(--float-tilt, 1deg))) scale(1, 1);
    animation-timing-function: cubic-bezier(0.33, 0.66, 0.66, 1);
  }
  90% {
    transform: translateY(calc(0.05 * var(--float-height, 6px))) translateX(0) rotate(0deg) scale(var(--float-squash-x, 1.02), var(--float-squash-y, 0.98));
    animation-timing-function: cubic-bezier(0.33, 0, 0.66, 1);
  }
  100% {
    transform: translateY(0) translateX(0) rotate(0deg) scale(var(--float-squash-x, 1.02), var(--float-squash-y, 0.98));
  }
}
@keyframes swing {
  0% {
    transform: rotate(0deg);
    animation-timing-function: cubic-bezier(0.2, 0, 0.8, 1);
  }
  8% {
    transform: rotate(var(--swing-angle, 22deg));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  18% {
    transform: rotate(calc(-1 * var(--swing-angle, 22deg) * 0.85));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  28% {
    transform: rotate(calc(var(--swing-angle, 22deg) * 0.65));
    animation-timing-function: cubic-bezier(0.35, 0, 0.65, 1);
  }
  38% {
    transform: rotate(calc(-1 * var(--swing-angle, 22deg) * 0.45));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  48% {
    transform: rotate(calc(var(--swing-angle, 22deg) * 0.25));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  56% {
    transform: rotate(calc(-1 * var(--swing-angle, 22deg) * 0.1));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  64% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(0deg);
  }
}
@keyframes jello {
  0% {
    transform: scale(1, 1);
    animation-timing-function: cubic-bezier(0.2, 0, 0.8, 1);
  }
  12% {
    transform: scale(var(--jello-scale-x, 1.15), calc(2 - var(--jello-scale-x, 1.15)));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  24% {
    transform: scale(calc(2 - var(--jello-scale-y, 1.12)), var(--jello-scale-y, 1.12));
    animation-timing-function: cubic-bezier(0.3, 0, 0.7, 1);
  }
  36% {
    transform: scale(calc(1 + (var(--jello-scale-x, 1.15) - 1) * 0.5), calc(2 - (1 + (var(--jello-scale-x, 1.15) - 1) * 0.5)));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  48% {
    transform: scale(calc(2 - (1 + (var(--jello-scale-y, 1.12) - 1) * 0.3)), calc(1 + (var(--jello-scale-y, 1.12) - 1) * 0.3));
    animation-timing-function: cubic-bezier(0.4, 0, 0.6, 1);
  }
  58% {
    transform: scale(1.02, 0.98);
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  68% {
    transform: scale(1, 1);
  }
  100% {
    transform: scale(1, 1);
  }
}
`;var To="",Wt="";function Je(){return To.replace(/\/$/,"")}function Ro(o){Wt=o}function Ze(){if(!Wt){let o=document.querySelector("[data-fa-kit-code]");o&&Ro(o.getAttribute("data-fa-kit-code")||"")}return Wt}var Qe="7.3.0";function Bo(o,t,e){let i="solid";return t==="chisel"&&(i="chisel-regular"),t==="etch"&&(i="etch-solid"),t==="graphite"&&(i="graphite-thin"),t==="jelly"&&(i="jelly-regular",e==="duo-regular"&&(i="jelly-duo-regular"),e==="fill-regular"&&(i="jelly-fill-regular")),t==="jelly-duo"&&(i="jelly-duo-regular"),t==="jelly-fill"&&(i="jelly-fill-regular"),t==="notdog"&&(e==="solid"&&(i="notdog-solid"),e==="duo-solid"&&(i="notdog-duo-solid")),t==="notdog-duo"&&(i="notdog-duo-solid"),t==="slab"&&((e==="solid"||e==="regular")&&(i="slab-regular"),e==="press-regular"&&(i="slab-press-regular")),t==="slab-press"&&(i="slab-press-regular"),t==="slab-duo"&&(i="slab-duo-regular"),t==="slab-press-duo"&&(i="slab-press-duo-regular"),t==="thumbprint"&&(i="thumbprint-light"),t==="utility"&&(i="utility-semibold"),t==="utility-duo"&&(i="utility-duo-semibold"),t==="utility-fill"&&(i="utility-fill-semibold"),t==="whiteboard"&&(i="whiteboard-semibold"),t==="mosaic"&&(i="mosaic-solid"),t==="pixel"&&(i="pixel-regular"),t==="vellum"&&(i="vellum-solid"),t==="classic"&&(e==="thin"&&(i="thin"),e==="light"&&(i="light"),e==="regular"&&(i="regular"),e==="solid"&&(i="solid")),t==="duotone"&&(e==="thin"&&(i="duotone-thin"),e==="light"&&(i="duotone-light"),e==="regular"&&(i="duotone-regular"),e==="solid"&&(i="duotone")),t==="sharp"&&(e==="thin"&&(i="sharp-thin"),e==="light"&&(i="sharp-light"),e==="regular"&&(i="sharp-regular"),e==="solid"&&(i="sharp-solid")),t==="sharp-duotone"&&(e==="thin"&&(i="sharp-duotone-thin"),e==="light"&&(i="sharp-duotone-light"),e==="regular"&&(i="sharp-duotone-regular"),e==="solid"&&(i="sharp-duotone-solid")),t==="brands"&&(i="brands"),i}function Oo(o,t,e){let i=Bo(o,t,e),a=Je();if(a)return`${a}/${i}/${o}.svg`;let r=Ze();return r.length>0?`https://ka-p.fontawesome.com/releases/v${Qe}/svgs/${i}/${o}.svg?token=${encodeURIComponent(r)}`:`https://ka-f.fontawesome.com/releases/v${Qe}/svgs/${i}/${o}.svg`}var No={name:"default",resolver:(o,t="classic",e="solid")=>Oo(o,t,e),mutator:(o,t)=>{if(o.hasAttribute("fill")||o.setAttribute("fill","currentColor"),t?.family&&!o.hasAttribute("data-duotone-initialized")){let{family:e,variant:i}=t;if(e==="duotone"||e==="sharp-duotone"||e==="notdog-duo"||e==="notdog"&&i==="duo-solid"||e==="jelly-duo"||e==="jelly"&&i==="duo-regular"||e==="utility-duo"||e==="slab-duo"||e==="slab-press-duo"||e==="thumbprint"){let a=[...o.querySelectorAll("path")],r=a.find(l=>!l.hasAttribute("opacity")),n=a.find(l=>l.hasAttribute("opacity"));if(!r||!n)return;if(r.setAttribute("data-duotone-primary",""),n.setAttribute("data-duotone-secondary",""),t.swapOpacity&&r&&n){let l=n.getAttribute("opacity")||"0.4";r.style.setProperty("--path-opacity",l),n.style.setProperty("--path-opacity","1")}o.setAttribute("data-duotone-initialized","")}}}},to=No;function qo(o){return`data:image/svg+xml,${encodeURIComponent(o)}`}var Xt={solid:{"arrow-down":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M169.4 502.6c12.5 12.5 32.8 12.5 45.3 0l160-160c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 402.7 224 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 370.7-105.4-105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160z"/></svg>',"arrow-up":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M214.6 9.4c-12.5-12.5-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 480c0 17.7 14.3 32 32 32s32-14.3 32-32l0-370.7 105.4 105.4c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-160-160z"/></svg>',backward:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M236.3 107.1C247.9 96 265 92.9 279.7 99.2C294.4 105.5 304 120 304 136L304 272.3L476.3 107.2C487.9 96 505 92.9 519.7 99.2C534.4 105.5 544 120 544 136L544 504C544 520 534.4 534.5 519.7 540.8C505 547.1 487.9 544 476.3 532.9L304 367.7L304 504C304 520 294.4 534.5 279.7 540.8C265 547.1 247.9 544 236.3 532.9L44.3 348.9C36.5 341.3 32 330.9 32 320C32 309.1 36.5 298.7 44.3 291.1L236.3 107.1z"/></svg>',"backward-step":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M491 100.8C478.1 93.8 462.3 94.5 450 102.6L192 272.1L192 128C192 110.3 177.7 96 160 96C142.3 96 128 110.3 128 128L128 512C128 529.7 142.3 544 160 544C177.7 544 192 529.7 192 512L192 367.9L450 537.5C462.3 545.6 478 546.3 491 539.3C504 532.3 512 518.8 512 504.1L512 136.1C512 121.4 503.9 107.9 491 100.9z"/></svg>',bars:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.3.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2026 Fonticons, Inc. --><path d="M0 96C0 78.3 14.3 64 32 64l384 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 128C14.3 128 0 113.7 0 96zM0 256c0-17.7 14.3-32 32-32l384 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 288c-17.7 0-32-14.3-32-32zM448 416c0 17.7-14.3 32-32 32L32 448c-17.7 0-32-14.3-32-32s14.3-32 32-32l384 0c17.7 0 32 14.3 32 32z"/></svg>',"angles-left":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M77.3 256 214.7 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256zm192 0L406.7 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L269.3 256z"/></svg>',"angles-right":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M434.7 256 297.3 118.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l160 160c12.5 12.5 12.5 32.8 0 45.3l-160 160c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L434.7 256zm-192 0L105.3 118.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l160 160c12.5 12.5 12.5 32.8 0 45.3l-160 160c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L242.7 256z"/></svg>',check:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M434.8 70.1c14.3 10.4 17.5 30.4 7.1 44.7l-256 352c-5.5 7.6-14 12.3-23.4 13.1s-18.5-2.7-25.1-9.3l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l101.5 101.5 234-321.7c10.4-14.3 30.4-17.5 44.7-7.1z"/></svg>',"chevron-down":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M201.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 338.7 54.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"/></svg>',"chevron-left":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l192 192c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256 246.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-192 192z"/></svg>',"chevron-right":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M311.1 233.4c12.5 12.5 12.5 32.8 0 45.3l-192 192c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L243.2 256 73.9 86.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l192 192z"/></svg>',circle:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0z"/></svg>',"closed-captioning":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M64 192C64 156.7 92.7 128 128 128L512 128C547.3 128 576 156.7 576 192L576 448C576 483.3 547.3 512 512 512L128 512C92.7 512 64 483.3 64 448L64 192zM216 272L248 272C252.4 272 256 275.6 256 280C256 293.3 266.7 304 280 304C293.3 304 304 293.3 304 280C304 249.1 278.9 224 248 224L216 224C185.1 224 160 249.1 160 280L160 360C160 390.9 185.1 416 216 416L248 416C278.9 416 304 390.9 304 360C304 346.7 293.3 336 280 336C266.7 336 256 346.7 256 360C256 364.4 252.4 368 248 368L216 368C211.6 368 208 364.4 208 360L208 280C208 275.6 211.6 272 216 272zM384 280C384 275.6 387.6 272 392 272L424 272C428.4 272 432 275.6 432 280C432 293.3 442.7 304 456 304C469.3 304 480 293.3 480 280C480 249.1 454.9 224 424 224L392 224C361.1 224 336 249.1 336 280L336 360C336 390.9 361.1 416 392 416L424 416C454.9 416 480 390.9 480 360C480 346.7 469.3 336 456 336C442.7 336 432 346.7 432 360C432 364.4 428.4 368 424 368L392 368C387.6 368 384 364.4 384 360L384 280z"/></svg>',"closed-captioning-slash":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M39 39.1C48.4 29.7 63.6 29.7 72.9 39.1L161.8 128L512 128C547.3 128 576 156.7 576 192L576 448C576 473.5 561.1 495.4 539.6 505.8L601 567.1C610.4 576.5 610.4 591.7 601 601C591.6 610.3 576.4 610.4 567.1 601L39 73.1C29.7 63.7 29.7 48.5 39 39.1zM384 350.1L384 279.9C384 275.5 387.6 271.9 392 271.9L424 271.9C428.4 271.9 432 275.5 432 279.9C432 293.2 442.7 303.9 456 303.9C469.3 303.9 480 293.2 480 279.9C480 249 454.9 223.9 424 223.9L392 223.9C361.1 223.9 336 249 336 279.9L336 302.1L384 350.1zM445.5 411.6C465.7 403.2 480 383.2 480 359.9C480 346.6 469.3 335.9 456 335.9C442.7 335.9 432 346.6 432 359.9C432 364.3 428.4 367.9 424 367.9L401.8 367.9L445.5 411.6zM162.3 264.1C160.8 269.1 160 274.5 160 280L160 360C160 390.9 185.1 416 216 416L248 416C266.1 416 282.1 407.5 292.4 394.2L410.2 512L128 512C92.7 512 64 483.3 64 448L64 192C64 184.2 65.4 176.7 68 169.8L162.3 264.1zM256.1 357.9C256 358.6 256 359.3 256 360C256 364.4 252.4 368 248 368L216 368C211.6 368 208 364.4 208 360L208 309.8L256.1 357.9z"/></svg>',compress:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M160 64c0-17.7-14.3-32-32-32S96 46.3 96 64l0 64-64 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c17.7 0 32-14.3 32-32l0-96zM32 320c-17.7 0-32 14.3-32 32s14.3 32 32 32l64 0 0 64c0 17.7 14.3 32 32 32s32-14.3 32-32l0-96c0-17.7-14.3-32-32-32l-96 0zM352 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32l96 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-64 0 0-64zM320 320c-17.7 0-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32s32-14.3 32-32l0-64 64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-96 0z"/></svg>',ellipsis:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M96 320C96 289.1 121.1 264 152 264C182.9 264 208 289.1 208 320C208 350.9 182.9 376 152 376C121.1 376 96 350.9 96 320zM264 320C264 289.1 289.1 264 320 264C350.9 264 376 289.1 376 320C376 350.9 350.9 376 320 376C289.1 376 264 350.9 264 320zM488 264C518.9 264 544 289.1 544 320C544 350.9 518.9 376 488 376C457.1 376 432 350.9 432 320C432 289.1 457.1 264 488 264z"/></svg>',"ellipsis-vertical":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M320 208C289.1 208 264 182.9 264 152C264 121.1 289.1 96 320 96C350.9 96 376 121.1 376 152C376 182.9 350.9 208 320 208zM320 432C350.9 432 376 457.1 376 488C376 518.9 350.9 544 320 544C289.1 544 264 518.9 264 488C264 457.1 289.1 432 320 432zM376 320C376 350.9 350.9 376 320 376C289.1 376 264 350.9 264 320C264 289.1 289.1 264 320 264C350.9 264 376 289.1 376 320z"/></svg>',expand:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 96C110.3 96 96 110.3 96 128L96 224C96 241.7 110.3 256 128 256C145.7 256 160 241.7 160 224L160 160L224 160C241.7 160 256 145.7 256 128C256 110.3 241.7 96 224 96L128 96zM160 416C160 398.3 145.7 384 128 384C110.3 384 96 398.3 96 416L96 512C96 529.7 110.3 544 128 544L224 544C241.7 544 256 529.7 256 512C256 494.3 241.7 480 224 480L160 480L160 416zM416 96C398.3 96 384 110.3 384 128C384 145.7 398.3 160 416 160L480 160L480 224C480 241.7 494.3 256 512 256C529.7 256 544 241.7 544 224L544 128C544 110.3 529.7 96 512 96L416 96zM544 416C544 398.3 529.7 384 512 384C494.3 384 480 398.3 480 416L480 480L416 480C398.3 480 384 494.3 384 512C384 529.7 398.3 544 416 544L512 544C529.7 544 544 529.7 544 512L544 416z"/></svg>',eyedropper:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M341.6 29.2l-101.6 101.6-9.4-9.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-9.4-9.4 101.6-101.6c39-39 39-102.2 0-141.1s-102.2-39-141.1 0zM55.4 323.3c-15 15-23.4 35.4-23.4 56.6l0 42.4-26.6 39.9c-8.5 12.7-6.8 29.6 4 40.4s27.7 12.5 40.4 4l39.9-26.6 42.4 0c21.2 0 41.6-8.4 56.6-23.4l109.4-109.4-45.3-45.3-109.4 109.4c-3 3-7.1 4.7-11.3 4.7l-36.1 0 0-36.1c0-4.2 1.7-8.3 4.7-11.3l109.4-109.4-45.3-45.3-109.4 109.4z"/></svg>',filter:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M32 64C19.1 64 7.4 71.8 2.4 83.8S.2 109.5 9.4 118.6L192 301.3 192 416c0 8.5 3.4 16.6 9.4 22.6l64 64c9.2 9.2 22.9 11.9 34.9 6.9S320 492.9 320 480l0-178.7 182.6-182.6c9.2-9.2 11.9-22.9 6.9-34.9S492.9 64 480 64L32 64z"/></svg>',forward:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M403.7 107.1C392.1 96 375 92.9 360.3 99.2C345.6 105.5 336 120 336 136L336 272.3L163.7 107.2C152.1 96 135 92.9 120.3 99.2C105.6 105.5 96 120 96 136L96 504C96 520 105.6 534.5 120.3 540.8C135 547.1 152.1 544 163.7 532.9L336 367.7L336 504C336 520 345.6 534.5 360.3 540.8C375 547.1 392.1 544 403.7 532.9L595.7 348.9C603.6 341.4 608 330.9 608 320C608 309.1 603.5 298.7 595.7 291.1L403.7 107.1z"/></svg>',file:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M192 64C156.7 64 128 92.7 128 128L128 512C128 547.3 156.7 576 192 576L448 576C483.3 576 512 547.3 512 512L512 234.5C512 217.5 505.3 201.2 493.3 189.2L386.7 82.7C374.7 70.7 358.5 64 341.5 64L192 64zM453.5 240L360 240C346.7 240 336 229.3 336 216L336 122.5L453.5 240z"/></svg>',"file-audio":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM389.8 307.7C380.7 301.4 368.3 303.6 362 312.7C355.7 321.8 357.9 334.2 367 340.5C390.9 357.2 406.4 384.8 406.4 416C406.4 447.2 390.8 474.9 367 491.5C357.9 497.8 355.7 510.3 362 519.3C368.3 528.3 380.8 530.6 389.8 524.3C423.9 500.5 446.4 460.8 446.4 416C446.4 371.2 424 331.5 389.8 307.7zM208 376C199.2 376 192 383.2 192 392L192 440C192 448.8 199.2 456 208 456L232 456L259.2 490C262.2 493.8 266.8 496 271.7 496L272 496C280.8 496 288 488.8 288 480L288 352C288 343.2 280.8 336 272 336L271.7 336C266.8 336 262.2 338.2 259.2 342L232 376L208 376zM336 448.2C336 458.9 346.5 466.4 354.9 459.8C367.8 449.5 376 433.7 376 416C376 398.3 367.8 382.5 354.9 372.2C346.5 365.5 336 373.1 336 383.8L336 448.3z"/></svg>',"file-code":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM282.2 359.6C290.8 349.5 289.7 334.4 279.6 325.8C269.5 317.2 254.4 318.3 245.8 328.4L197.8 384.4C190.1 393.4 190.1 406.6 197.8 415.6L245.8 471.6C254.4 481.7 269.6 482.8 279.6 474.2C289.6 465.6 290.8 450.4 282.2 440.4L247.6 400L282.2 359.6zM394.2 328.4C385.6 318.3 370.4 317.2 360.4 325.8C350.4 334.4 349.2 349.6 357.8 359.6L392.4 400L357.8 440.4C349.2 450.5 350.3 465.6 360.4 474.2C370.5 482.8 385.6 481.7 394.2 471.6L442.2 415.6C449.9 406.6 449.9 393.4 442.2 384.4L394.2 328.4z"/></svg>',"file-excel":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM292 330.7C284.6 319.7 269.7 316.7 258.7 324C247.7 331.3 244.7 346.3 252 357.3L291.2 416L252 474.7C244.6 485.7 247.6 500.6 258.7 508C269.8 515.4 284.6 512.4 292 501.3L320 459.3L348 501.3C355.4 512.3 370.3 515.3 381.3 508C392.3 500.7 395.3 485.7 388 474.7L348.8 416L388 357.3C395.4 346.3 392.4 331.4 381.3 324C370.2 316.6 355.4 319.6 348 330.7L320 372.7L292 330.7z"/></svg>',"file-image":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM256 320C256 302.3 241.7 288 224 288C206.3 288 192 302.3 192 320C192 337.7 206.3 352 224 352C241.7 352 256 337.7 256 320zM220.6 512L419.4 512C435.2 512 448 499.2 448 483.4C448 476.1 445.2 469 440.1 463.7L343.3 361.9C337.3 355.6 328.9 352 320.1 352L319.8 352C311 352 302.7 355.6 296.6 361.9L199.9 463.7C194.8 469 192 476.1 192 483.4C192 499.2 204.8 512 220.6 512z"/></svg>',"file-pdf":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 64C92.7 64 64 92.7 64 128L64 512C64 547.3 92.7 576 128 576L208 576L208 464C208 428.7 236.7 400 272 400L448 400L448 234.5C448 217.5 441.3 201.2 429.3 189.2L322.7 82.7C310.7 70.7 294.5 64 277.5 64L128 64zM389.5 240L296 240C282.7 240 272 229.3 272 216L272 122.5L389.5 240zM272 444C261 444 252 453 252 464L252 592C252 603 261 612 272 612C283 612 292 603 292 592L292 564L304 564C337.1 564 364 537.1 364 504C364 470.9 337.1 444 304 444L272 444zM304 524L292 524L292 484L304 484C315 484 324 493 324 504C324 515 315 524 304 524zM400 444C389 444 380 453 380 464L380 592C380 603 389 612 400 612L432 612C460.7 612 484 588.7 484 560L484 496C484 467.3 460.7 444 432 444L400 444zM420 572L420 484L432 484C438.6 484 444 489.4 444 496L444 560C444 566.6 438.6 572 432 572L420 572zM508 464L508 592C508 603 517 612 528 612C539 612 548 603 548 592L548 548L576 548C587 548 596 539 596 528C596 517 587 508 576 508L548 508L548 484L576 484C587 484 596 475 596 464C596 453 587 444 576 444L528 444C517 444 508 453 508 464z"/></svg>',"file-powerpoint":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM280 320C266.7 320 256 330.7 256 344L256 488C256 501.3 266.7 512 280 512C293.3 512 304 501.3 304 488L304 464L328 464C367.8 464 400 431.8 400 392C400 352.2 367.8 320 328 320L280 320zM328 416L304 416L304 368L328 368C341.3 368 352 378.7 352 392C352 405.3 341.3 416 328 416z"/></svg>',"file-video":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM208 368L208 464C208 481.7 222.3 496 240 496L336 496C353.7 496 368 481.7 368 464L368 440L403 475C406.2 478.2 410.5 480 415 480C424.4 480 432 472.4 432 463L432 368.9C432 359.5 424.4 351.9 415 351.9C410.5 351.9 406.2 353.7 403 356.9L368 391.9L368 367.9C368 350.2 353.7 335.9 336 335.9L240 335.9C222.3 335.9 208 350.2 208 367.9z"/></svg>',"file-word":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM263.4 338.8C260.5 325.9 247.7 317.7 234.8 320.6C221.9 323.5 213.7 336.3 216.6 349.2L248.6 493.2C250.9 503.7 260 511.4 270.8 512C281.6 512.6 291.4 505.9 294.8 495.6L320 419.9L345.2 495.6C348.6 505.8 358.4 512.5 369.2 512C380 511.5 389.1 503.8 391.4 493.2L423.4 349.2C426.3 336.3 418.1 323.4 405.2 320.6C392.3 317.8 379.4 325.9 376.6 338.8L363.4 398.2L342.8 336.4C339.5 326.6 330.4 320 320 320C309.6 320 300.5 326.6 297.2 336.4L276.6 398.2L263.4 338.8z"/></svg>',"file-zipper":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM192 136C192 149.3 202.7 160 216 160L264 160C277.3 160 288 149.3 288 136C288 122.7 277.3 112 264 112L216 112C202.7 112 192 122.7 192 136zM192 232C192 245.3 202.7 256 216 256L264 256C277.3 256 288 245.3 288 232C288 218.7 277.3 208 264 208L216 208C202.7 208 192 218.7 192 232zM256 304L224 304C206.3 304 192 318.3 192 336L192 384C192 410.5 213.5 432 240 432C266.5 432 288 410.5 288 384L288 336C288 318.3 273.7 304 256 304zM240 368C248.8 368 256 375.2 256 384C256 392.8 248.8 400 240 400C231.2 400 224 392.8 224 384C224 375.2 231.2 368 240 368z"/></svg>',"forward-step":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M21 36.8c12.9-7 28.7-6.3 41 1.8L320 208.1 320 64c0-17.7 14.3-32 32-32s32 14.3 32 32l0 384c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-144.1-258 169.6c-12.3 8.1-28 8.8-41 1.8S0 454.7 0 440L0 72C0 57.3 8.1 43.8 21 36.8z"/></svg>',gauge:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zm320 96c0-26.9-16.5-49.9-40-59.3L280 120c0-13.3-10.7-24-24-24s-24 10.7-24 24l0 172.7c-23.5 9.5-40 32.5-40 59.3 0 35.3 28.7 64 64 64s64-28.7 64-64zM144 176a32 32 0 1 0 0-64 32 32 0 1 0 0 64zm-16 80a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm288 32a32 32 0 1 0 0-64 32 32 0 1 0 0 64zM400 144a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"/></svg>',gear:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M259.1 73.5C262.1 58.7 275.2 48 290.4 48L350.2 48C365.4 48 378.5 58.7 381.5 73.5L396 143.5C410.1 149.5 423.3 157.2 435.3 166.3L503.1 143.8C517.5 139 533.3 145 540.9 158.2L570.8 210C578.4 223.2 575.7 239.8 564.3 249.9L511 297.3C511.9 304.7 512.3 312.3 512.3 320C512.3 327.7 511.8 335.3 511 342.7L564.4 390.2C575.8 400.3 578.4 417 570.9 430.1L541 481.9C533.4 495 517.6 501.1 503.2 496.3L435.4 473.8C423.3 482.9 410.1 490.5 396.1 496.6L381.7 566.5C378.6 581.4 365.5 592 350.4 592L290.6 592C275.4 592 262.3 581.3 259.3 566.5L244.9 496.6C230.8 490.6 217.7 482.9 205.6 473.8L137.5 496.3C123.1 501.1 107.3 495.1 99.7 481.9L69.8 430.1C62.2 416.9 64.9 400.3 76.3 390.2L129.7 342.7C128.8 335.3 128.4 327.7 128.4 320C128.4 312.3 128.9 304.7 129.7 297.3L76.3 249.8C64.9 239.7 62.3 223 69.8 209.9L99.7 158.1C107.3 144.9 123.1 138.9 137.5 143.7L205.3 166.2C217.4 157.1 230.6 149.5 244.6 143.4L259.1 73.5zM320.3 400C364.5 399.8 400.2 363.9 400 319.7C399.8 275.5 363.9 239.8 319.7 240C275.5 240.2 239.8 276.1 240 320.3C240.2 364.5 276.1 400.2 320.3 400z"/></svg>',"grip-vertical":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M128 40c0-22.1-17.9-40-40-40L40 0C17.9 0 0 17.9 0 40L0 88c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48zm0 192c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48zM0 424l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM320 40c0-22.1-17.9-40-40-40L232 0c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48zM192 232l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM320 424c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48z"/></svg>',indeterminate:'<svg part="indeterminate-icon" class="icon" viewBox="0 0 16 16"><g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round"><g stroke="currentColor" stroke-width="2"><g transform="translate(2.285714 6.857143)"><path d="M10.2857143,1.14285714 L1.14285714,1.14285714"/></g></g></g></svg>',"magnifying-glass":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376C296.3 401.1 253.9 416 208 416 93.1 416 0 322.9 0 208S93.1 0 208 0 416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/></svg>',minus:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M0 256c0-17.7 14.3-32 32-32l384 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 288c-17.7 0-32-14.3-32-32z"/></svg>',pause:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M48 32C21.5 32 0 53.5 0 80L0 432c0 26.5 21.5 48 48 48l64 0c26.5 0 48-21.5 48-48l0-352c0-26.5-21.5-48-48-48L48 32zm224 0c-26.5 0-48 21.5-48 48l0 352c0 26.5 21.5 48 48 48l64 0c26.5 0 48-21.5 48-48l0-352c0-26.5-21.5-48-48-48l-64 0z"/></svg>',"picture-in-picture":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M448 32c35.3 0 64 28.7 64 64l0 112-64 0 0-112-384 0 0 320 144 0 0 64-144 0-6.5-.3c-30.1-3.1-54.1-27-57.1-57.1L0 416 0 96C0 62.9 25.2 35.6 57.5 32.3L64 32 448 32zm16 224c26.5 0 48 21.5 48 48l0 128c0 26.5-21.5 48-48 48l-160 0c-26.5 0-48-21.5-48-48l0-128c0-26.5 21.5-48 48-48l160 0z"/></svg>',play:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M91.2 36.9c-12.4-6.8-27.4-6.5-39.6 .7S32 57.9 32 72l0 368c0 14.1 7.5 27.2 19.6 34.4s27.2 7.5 39.6 .7l336-184c12.8-7 20.8-20.5 20.8-35.1s-8-28.1-20.8-35.1l-336-184z"/></svg>',"play-circle":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zM188.3 147.1c-7.6 4.2-12.3 12.3-12.3 20.9l0 176c0 8.7 4.7 16.7 12.3 20.9s16.8 4.1 24.3-.5l144-88c7.1-4.4 11.5-12.1 11.5-20.5s-4.4-16.1-11.5-20.5l-144-88c-7.4-4.5-16.7-4.7-24.3-.5z"/></svg>',plus:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M352 128C352 110.3 337.7 96 320 96C302.3 96 288 110.3 288 128L288 288L128 288C110.3 288 96 302.3 96 320C96 337.7 110.3 352 128 352L288 352L288 512C288 529.7 302.3 544 320 544C337.7 544 352 529.7 352 512L352 352L512 352C529.7 352 544 337.7 544 320C544 302.3 529.7 288 512 288L352 288L352 128z"/></svg>',star:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M309.5-18.9c-4.1-8-12.4-13.1-21.4-13.1s-17.3 5.1-21.4 13.1L193.1 125.3 33.2 150.7c-8.9 1.4-16.3 7.7-19.1 16.3s-.5 18 5.8 24.4l114.4 114.5-25.2 159.9c-1.4 8.9 2.3 17.9 9.6 23.2s16.9 6.1 25 2L288.1 417.6 432.4 491c8 4.1 17.7 3.3 25-2s11-14.2 9.6-23.2L441.7 305.9 556.1 191.4c6.4-6.4 8.6-15.8 5.8-24.4s-10.1-14.9-19.1-16.3L383 125.3 309.5-18.9z"/></svg>',"table-columns":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M0 96C0 60.7 28.7 32 64 32l320 0c35.3 0 64 28.7 64 64l0 320c0 35.3-28.7 64-64 64L64 480c-35.3 0-64-28.7-64-64L0 96zm64 64l0 256 128 0 0-256-128 0zm320 0l-128 0 0 256 128 0 0-256z"/></svg>',thumbtack:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M32 32C32 14.3 46.3 0 64 0L320 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-29.5 0 10.3 134.1c37.1 21.2 65.8 56.4 78.2 99.7l3.8 13.4c2.8 9.7 .8 20-5.2 28.1S362 352 352 352L32 352c-10 0-19.5-4.7-25.5-12.7s-8-18.4-5.2-28.1L5 297.8c12.4-43.3 41-78.5 78.2-99.7L93.5 64 64 64C46.3 64 32 49.7 32 32zM160 400l64 0 0 112c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-112z"/></svg>',"up-down":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M406.6 502.6l96-96c9.2-9.2 11.9-22.9 6.9-34.9S492.9 352 480 352l-64 0 0-320c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 320-64 0c-12.9 0-24.6 7.8-29.6 19.8s-2.2 25.7 6.9 34.9l96 96c12.5 12.5 32.8 12.5 45.3 0zM150.6 9.4c-12.5-12.5-32.8-12.5-45.3 0l-96 96c-9.2 9.2-11.9 22.9-6.9 34.9S19.1 160 32 160l64 0 0 320c0 17.7 14.3 32 32 32s32-14.3 32-32l0-320 64 0c12.9 0 24.6-7.8 29.6-19.8s2.2-25.7-6.9-34.9l-96-96z"/></svg>',upload:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M352 173.3L352 384C352 401.7 337.7 416 320 416C302.3 416 288 401.7 288 384L288 173.3L246.6 214.7C234.1 227.2 213.8 227.2 201.3 214.7C188.8 202.2 188.8 181.9 201.3 169.4L297.3 73.4C309.8 60.9 330.1 60.9 342.6 73.4L438.6 169.4C451.1 181.9 451.1 202.2 438.6 214.7C426.1 227.2 405.8 227.2 393.3 214.7L352 173.3zM320 464C364.2 464 400 428.2 400 384L480 384C515.3 384 544 412.7 544 448L544 480C544 515.3 515.3 544 480 544L160 544C124.7 544 96 515.3 96 480L96 448C96 412.7 124.7 384 160 384L240 384C240 428.2 275.8 464 320 464zM464 488C477.3 488 488 477.3 488 464C488 450.7 477.3 440 464 440C450.7 440 440 450.7 440 464C440 477.3 450.7 488 464 488z"/></svg>',user:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M224 248a120 120 0 1 0 0-240 120 120 0 1 0 0 240zm-29.7 56C95.8 304 16 383.8 16 482.3 16 498.7 29.3 512 45.7 512l356.6 0c16.4 0 29.7-13.3 29.7-29.7 0-98.5-79.8-178.3-178.3-178.3l-59.4 0z"/></svg>',volume:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M48 352l48 0 134.1 119.2c6.4 5.7 14.6 8.8 23.1 8.8 19.2 0 34.8-15.6 34.8-34.8l0-378.4c0-19.2-15.6-34.8-34.8-34.8-8.5 0-16.7 3.1-23.1 8.8L96 160 48 160c-26.5 0-48 21.5-48 48l0 96c0 26.5 21.5 48 48 48zM441.1 107c-10.3-8.4-25.4-6.8-33.8 3.5s-6.8 25.4 3.5 33.8C443.3 170.7 464 210.9 464 256s-20.7 85.3-53.2 111.8c-10.3 8.4-11.8 23.5-3.5 33.8s23.5 11.8 33.8 3.5c43.2-35.2 70.9-88.9 70.9-149s-27.7-113.8-70.9-149zm-60.5 74.5c-10.3-8.4-25.4-6.8-33.8 3.5s-6.8 25.4 3.5 33.8C361.1 227.6 368 241 368 256s-6.9 28.4-17.7 37.3c-10.3 8.4-11.8 23.5-3.5 33.8s23.5 11.8 33.8 3.5C402.1 312.9 416 286.1 416 256s-13.9-56.9-35.5-74.5z"/></svg>',"volume-low":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M48 352l48 0 134.1 119.2c6.4 5.7 14.6 8.8 23.1 8.8 19.2 0 34.8-15.6 34.8-34.8l0-378.4c0-19.2-15.6-34.8-34.8-34.8-8.5 0-16.7 3.1-23.1 8.8L96 160 48 160c-26.5 0-48 21.5-48 48l0 96c0 26.5 21.5 48 48 48zM380.6 181.5c-10.3-8.4-25.4-6.8-33.8 3.5s-6.8 25.4 3.5 33.8C361.1 227.6 368 241 368 256s-6.9 28.4-17.7 37.3c-10.3 8.4-11.8 23.5-3.5 33.8s23.5 11.8 33.8 3.5C402.1 312.9 416 286.1 416 256s-13.9-56.9-35.5-74.5z"/></svg>',"volume-xmark":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M48 352l48 0 134.1 119.2c6.4 5.7 14.6 8.8 23.1 8.8 19.2 0 34.8-15.6 34.8-34.8l0-378.4c0-19.2-15.6-34.8-34.8-34.8-8.5 0-16.7 3.1-23.1 8.8L96 160 48 160c-26.5 0-48 21.5-48 48l0 96c0 26.5 21.5 48 48 48zM367 175c-9.4 9.4-9.4 24.6 0 33.9l47 47-47 47c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l47-47 47 47c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-47-47 47-47c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-47 47-47-47c-9.4-9.4-24.6-9.4-33.9 0z"/></svg>',xmark:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M55.1 73.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L147.2 256 9.9 393.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192.5 301.3 329.9 438.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.8 256 375.1 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192.5 210.7 55.1 73.4z"/></svg>'},regular:{calendar:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M216 64C229.3 64 240 74.7 240 88L240 128L400 128L400 88C400 74.7 410.7 64 424 64C437.3 64 448 74.7 448 88L448 128L480 128C515.3 128 544 156.7 544 192L544 480C544 515.3 515.3 544 480 544L160 544C124.7 544 96 515.3 96 480L96 192C96 156.7 124.7 128 160 128L192 128L192 88C192 74.7 202.7 64 216 64zM216 176L160 176C151.2 176 144 183.2 144 192L144 240L496 240L496 192C496 183.2 488.8 176 480 176L216 176zM144 288L144 480C144 488.8 151.2 496 160 496L480 496C488.8 496 496 488.8 496 480L496 288L144 288z"/></svg>',"circle-question":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M464 256a208 208 0 1 0 -416 0 208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zm256-80c-17.7 0-32 14.3-32 32 0 13.3-10.7 24-24 24s-24-10.7-24-24c0-44.2 35.8-80 80-80s80 35.8 80 80c0 47.2-36 67.2-56 74.5l0 3.8c0 13.3-10.7 24-24 24s-24-10.7-24-24l0-8.1c0-20.5 14.8-35.2 30.1-40.2 6.4-2.1 13.2-5.5 18.2-10.3 4.3-4.2 7.7-10 7.7-19.6 0-17.7-14.3-32-32-32zM224 368a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/></svg>',"circle-xmark":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464a256 256 0 1 0 0-512 256 256 0 1 0 0 512zM167 167c-9.4 9.4-9.4 24.6 0 33.9l55 55-55 55c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l55-55 55 55c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-55-55 55-55c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-55 55-55-55c-9.4-9.4-24.6-9.4-33.9 0z"/></svg>',clock:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M528 320C528 434.9 434.9 528 320 528C205.1 528 112 434.9 112 320C112 205.1 205.1 112 320 112C434.9 112 528 205.1 528 320zM64 320C64 461.4 178.6 576 320 576C461.4 576 576 461.4 576 320C576 178.6 461.4 64 320 64C178.6 64 64 178.6 64 320zM296 184L296 320C296 328 300 335.5 306.7 340L402.7 404C413.7 411.4 428.6 408.4 436 397.3C443.4 386.2 440.4 371.4 429.3 364L344 307.2L344 184C344 170.7 333.3 160 320 160C306.7 160 296 170.7 296 184z"/></svg>',copy:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M384 336l-192 0c-8.8 0-16-7.2-16-16l0-256c0-8.8 7.2-16 16-16l133.5 0c4.2 0 8.3 1.7 11.3 4.7l58.5 58.5c3 3 4.7 7.1 4.7 11.3L400 320c0 8.8-7.2 16-16 16zM192 384l192 0c35.3 0 64-28.7 64-64l0-197.5c0-17-6.7-33.3-18.7-45.3L370.7 18.7C358.7 6.7 342.5 0 325.5 0L192 0c-35.3 0-64 28.7-64 64l0 256c0 35.3 28.7 64 64 64zM64 128c-35.3 0-64 28.7-64 64L0 448c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-16-48 0 0 16c0 8.8-7.2 16-16 16L64 464c-8.8 0-16-7.2-16-16l0-256c0-8.8 7.2-16 16-16l16 0 0-48-16 0z"/></svg>',eye:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M288 80C222.8 80 169.2 109.6 128.1 147.7 89.6 183.5 63 226 49.4 256 63 286 89.6 328.5 128.1 364.3 169.2 402.4 222.8 432 288 432s118.8-29.6 159.9-67.7C486.4 328.5 513 286 526.6 256 513 226 486.4 183.5 447.9 147.7 406.8 109.6 353.2 80 288 80zM95.4 112.6C142.5 68.8 207.2 32 288 32s145.5 36.8 192.6 80.6c46.8 43.5 78.1 95.4 93 131.1 3.3 7.9 3.3 16.7 0 24.6-14.9 35.7-46.2 87.7-93 131.1-47.1 43.7-111.8 80.6-192.6 80.6S142.5 443.2 95.4 399.4c-46.8-43.5-78.1-95.4-93-131.1-3.3-7.9-3.3-16.7 0-24.6 14.9-35.7 46.2-87.7 93-131.1zM288 336c44.2 0 80-35.8 80-80 0-29.6-16.1-55.5-40-69.3-1.4 59.7-49.6 107.9-109.3 109.3 13.8 23.9 39.7 40 69.3 40zm-79.6-88.4c2.5 .3 5 .4 7.6 .4 35.3 0 64-28.7 64-64 0-2.6-.2-5.1-.4-7.6-37.4 3.9-67.2 33.7-71.1 71.1zm45.6-115c10.8-3 22.2-4.5 33.9-4.5 8.8 0 17.5 .9 25.8 2.6 .3 .1 .5 .1 .8 .2 57.9 12.2 101.4 63.7 101.4 125.2 0 70.7-57.3 128-128 128-61.6 0-113-43.5-125.2-101.4-1.8-8.6-2.8-17.5-2.8-26.6 0-11 1.4-21.8 4-32 .2-.7 .3-1.3 .5-1.9 11.9-43.4 46.1-77.6 89.5-89.5z"/></svg>',"eye-slash":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M41-24.9c-9.4-9.4-24.6-9.4-33.9 0S-2.3-.3 7 9.1l528 528c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-96.4-96.4c2.7-2.4 5.4-4.8 8-7.2 46.8-43.5 78.1-95.4 93-131.1 3.3-7.9 3.3-16.7 0-24.6-14.9-35.7-46.2-87.7-93-131.1-47.1-43.7-111.8-80.6-192.6-80.6-56.8 0-105.6 18.2-146 44.2L41-24.9zM176.9 111.1c32.1-18.9 69.2-31.1 111.1-31.1 65.2 0 118.8 29.6 159.9 67.7 38.5 35.7 65.1 78.3 78.6 108.3-13.6 30-40.2 72.5-78.6 108.3-3.1 2.8-6.2 5.6-9.4 8.4L393.8 328c14-20.5 22.2-45.3 22.2-72 0-70.7-57.3-128-128-128-26.7 0-51.5 8.2-72 22.2l-39.1-39.1zm182 182l-108-108c11.1-5.8 23.7-9.1 37.1-9.1 44.2 0 80 35.8 80 80 0 13.4-3.3 26-9.1 37.1zM103.4 173.2l-34-34c-32.6 36.8-55 75.8-66.9 104.5-3.3 7.9-3.3 16.7 0 24.6 14.9 35.7 46.2 87.7 93 131.1 47.1 43.7 111.8 80.6 192.6 80.6 37.3 0 71.2-7.9 101.5-20.6L352.2 422c-20 6.4-41.4 10-64.2 10-65.2 0-118.8-29.6-159.9-67.7-38.5-35.7-65.1-78.3-78.6-108.3 10.4-23.1 28.6-53.6 54-82.8z"/></svg>',star:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M288.1-32c9 0 17.3 5.1 21.4 13.1L383 125.3 542.9 150.7c8.9 1.4 16.3 7.7 19.1 16.3s.5 18-5.8 24.4L441.7 305.9 467 465.8c1.4 8.9-2.3 17.9-9.6 23.2s-17 6.1-25 2L288.1 417.6 143.8 491c-8 4.1-17.7 3.3-25-2s-11-14.2-9.6-23.2L134.4 305.9 20 191.4c-6.4-6.4-8.6-15.8-5.8-24.4s10.1-14.9 19.1-16.3l159.9-25.4 73.6-144.2c4.1-8 12.4-13.1 21.4-13.1zm0 76.8L230.3 158c-3.5 6.8-10 11.6-17.6 12.8l-125.5 20 89.8 89.9c5.4 5.4 7.9 13.1 6.7 20.7l-19.8 125.5 113.3-57.6c6.8-3.5 14.9-3.5 21.8 0l113.3 57.6-19.8-125.5c-1.2-7.6 1.3-15.3 6.7-20.7l89.8-89.9-125.5-20c-7.6-1.2-14.1-6-17.6-12.8L288.1 44.8z"/></svg>'}},Uo={name:"system",resolver:(o,t="classic",e="solid")=>{let a=Xt[e][o]??Xt.regular[o]??Xt.regular["circle-question"];return a?qo(a):""},mutator:o=>{o.hasAttribute("fill")||o.setAttribute("fill","currentColor")}},eo=Uo;var Vo="classic",Ho=[to,eo],oo=new Set;function io(o){oo.add(o)}function ao(o){oo.delete(o)}function St(o){return Ho.find(t=>t.name===o)}function ro(){return Vo}var jo=Object.defineProperty,Wo=Object.getOwnPropertyDescriptor,b=(o,t,e,i)=>{for(var a=i>1?void 0:i?Wo(t,e):t,r=o.length-1,n;r>=0;r--)(n=o[r])&&(a=(i?n(t,e,a):n(a))||a);return i&&a&&jo(t,e,a),a},rt=Symbol(),At=Symbol(),Yt,Kt=new Map,w=class extends x{constructor(){super(...arguments),this.svg=null,this.autoWidth=!1,this.swapOpacity=!1,this.label="",this.library="default",this.rotate=0,this.resolveIcon=async(o,t)=>{let e;if(t?.spriteSheet){this.hasUpdated||await this.updateComplete,this.svg=p`<svg part="svg">
        <use part="use" href="${o}"></use>
      </svg>`,await this.updateComplete;let i=this.shadowRoot.querySelector("[part='svg']");return typeof t.mutator=="function"&&t.mutator(i,this),this.svg}try{if(e=await fetch(o,{mode:"cors"}),!e.ok)return e.status===410?rt:At}catch{return At}try{let i=document.createElement("div");i.innerHTML=await e.text();let a=i.firstElementChild;if(a?.tagName?.toLowerCase()!=="svg")return rt;Yt||(Yt=new DOMParser);let n=Yt.parseFromString(a.outerHTML,"text/html").body.querySelector("svg");return n?(n.part.add("svg"),document.adoptNode(n)):rt}catch{return rt}}}connectedCallback(){super.connectedCallback(),io(this)}firstUpdated(o){super.firstUpdated(o),this.hasAttribute("rotate")&&this.style.setProperty("--rotate-angle",`${this.rotate}deg`),this.setIcon()}disconnectedCallback(){super.disconnectedCallback(),ao(this)}async getIconSource(){let o=St(this.library),t=this.family||ro();if(this.name&&o){let e=this.canvas==="auto"||this.autoWidth,i;try{i=await o.resolver(this.name,t,this.variant,e)}catch{i=void 0}return{url:i,fromLibrary:!0}}return{url:this.src,fromLibrary:!1}}handleLabelChange(){typeof this.label=="string"&&this.label.length>0?(this.setAttribute("role","img"),this.setAttribute("aria-label",this.label),this.removeAttribute("aria-hidden")):(this.removeAttribute("role"),this.removeAttribute("aria-label"),this.setAttribute("aria-hidden","true"))}async setIcon(){let{url:o,fromLibrary:t}=await this.getIconSource(),e=t?St(this.library):void 0;if(!o){this.svg=null;return}let i=Kt.get(o);i||(i=this.resolveIcon(o,e),Kt.set(o,i));let a=await i;a===At&&Kt.delete(o);let r=await this.getIconSource();if(o===r.url){if(Le(a)){this.svg=a;return}switch(a){case At:case rt:this.svg=null,this.dispatchEvent(new $t);break;default:this.svg=a.cloneNode(!0),e?.mutator?.(this.svg,this),this.dispatchEvent(new zt)}}}willUpdate(o){return this.style||this.setStyleProperty("--rotate-angle",`${this.rotate}deg`),super.willUpdate(o)}updated(o){super.updated(o);let t=St(this.library);this.hasAttribute("rotate")&&this.style.setProperty("--rotate-angle",`${this.rotate}deg`);let e=this.shadowRoot?.querySelector("svg");e&&t?.mutator?.(e,this)}render(){return this.hasUpdated?this.svg:p`<svg part="svg" width="16" height="16" viewBox="0 0 16 16"></svg>`}};w.css=Ge;b([et()],w.prototype,"svg",2);b([c({reflect:!0})],w.prototype,"name",2);b([c({reflect:!0})],w.prototype,"family",2);b([c({reflect:!0})],w.prototype,"variant",2);b([c({reflect:!0})],w.prototype,"canvas",2);b([c({attribute:"auto-width",type:Boolean,reflect:!0})],w.prototype,"autoWidth",2);b([c({attribute:"swap-opacity",type:Boolean,reflect:!0})],w.prototype,"swapOpacity",2);b([c()],w.prototype,"src",2);b([c()],w.prototype,"label",2);b([c({reflect:!0})],w.prototype,"library",2);b([c({type:Number,reflect:!0})],w.prototype,"rotate",2);b([c({type:String,reflect:!0})],w.prototype,"flip",2);b([c({type:String,reflect:!0})],w.prototype,"animation",2);b([F("label")],w.prototype,"handleLabelChange",1);b([F(["family","name","library","variant","src","autoWidth","canvas","swapOpacity"],{waitUntilFirstUpdate:!0})],w.prototype,"setIcon",1);w=b([k("wa-icon")],w);var no=v`:host {
  --track-width: 2px;
  --track-color: var(--wa-color-neutral-fill-normal);
  --indicator-color: var(--wa-color-brand-fill-loud);
  --speed: 2s;
  --size: 1em;
  flex: none;
  display: inline-flex;
  width: var(--size);
  height: var(--size);
}
svg {
  width: 100%;
  height: 100%;
  aspect-ratio: 1;
  animation: spin var(--speed) linear infinite;
}
.track,
.indicator {
  --radius: calc(var(--size) / 2 - var(--track-width) / 2);
  --circumference: calc(var(--radius) * 2 * 3.141592654);
  cx: calc(var(--size) / 2);
  cy: calc(var(--size) / 2);
  r: var(--radius);
  fill: none;
  stroke-width: var(--track-width);
}
.track {
  stroke: var(--track-color);
}
.indicator {
  stroke: var(--indicator-color);
  stroke-linecap: round;
  stroke-dasharray: calc(0.597 * var(--circumference)), calc(0.796 * var(--circumference));
  stroke-dashoffset: calc(-0.04 * var(--circumference));
  animation: dash 1.5s ease-in-out infinite;
}
@media (prefers-reduced-motion: reduce) {
  svg,
  .indicator {
    animation: none;
  }
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
@keyframes dash {
  0% {
    stroke-dasharray: calc(0.008 * var(--circumference)), calc(1.194 * var(--circumference));
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: calc(0.716 * var(--circumference)), calc(1.194 * var(--circumference));
    stroke-dashoffset: calc(-0.278 * var(--circumference));
  }
  100% {
    stroke-dasharray: calc(0.716 * var(--circumference)), calc(1.194 * var(--circumference));
    stroke-dashoffset: calc(-0.987 * var(--circumference));
  }
}
`;var Xo=Object.defineProperty,Yo=Object.getOwnPropertyDescriptor,Ko=(o,t,e,i)=>{for(var a=i>1?void 0:i?Yo(t,e):t,r=o.length-1,n;r>=0;r--)(n=o[r])&&(a=(i?n(t,e,a):n(a))||a);return i&&a&&Xo(t,e,a),a},Gt=class extends x{constructor(){super(...arguments),this.localize=new X(this)}render(){return p`
      <svg
        part="base spinner"
        role="progressbar"
        aria-label=${this.localize.term("loading")}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle class="track" />
        <circle class="indicator" />
      </svg>
    `}};Gt.css=no;Gt=Ko([k("wa-spinner")],Gt);var so=v`@layer wa-component {
  :host {
    display: inline-block;
  }
  :host:has(wa-badge) {
    position: relative;
  }
  :host(:has(wa-badge)) {
    position: relative;
  }
}
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  user-select: none;
  -webkit-user-select: none;
  white-space: nowrap;
  vertical-align: middle;
  transition-property:
    background,
    border,
    box-shadow,
    color,
    opacity,
    transform;
  transition-duration: var(--wa-transition-fast);
  transition-timing-function: var(--wa-transition-easing);
  transform-origin: center;
  cursor: pointer;
  padding: 0 var(--wa-form-control-padding-inline);
  font-family: inherit;
  font-size: inherit;
  font-weight: var(--wa-font-weight-action);
  height: var(--wa-form-control-height);
  width: 100%;
  background-color: var(--wa-color-fill-loud, var(--wa-color-neutral-fill-loud));
  border-color: transparent;
  color: var(--wa-color-on-loud, var(--wa-color-neutral-on-loud));
  border-start-start-radius: var(--_button-start-start-radius, var(--wa-form-control-border-radius));
  border-start-end-radius: var(--_button-start-end-radius, var(--wa-form-control-border-radius));
  border-end-start-radius: var(--_button-end-start-radius, var(--wa-form-control-border-radius));
  border-end-end-radius: var(--_button-end-end-radius, var(--wa-form-control-border-radius));
  border-style: var(--wa-form-control-border-style);
  border-width: var(--wa-form-control-border-width);
}
@media (hover: hover) {
  .button:not(.disabled):not(.loading):hover {
    transform: var(--wa-button-transform-hover);
  }
}
.button:not(.disabled):not(.loading):active {
  transform: var(--wa-button-transform-active);
}
@media (prefers-reduced-motion: reduce) {
  .button:not(.disabled):not(.loading):hover,
  .button:not(.disabled):not(.loading):active {
    transform: none;
  }
}
:host([appearance="plain"]) {
  margin-inline-start: var(--_button-horizontal-indent);
  margin-block-start: var(--_button-vertical-indent);
}
:host([appearance="plain"]) .button {
  color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
  background-color: transparent;
  border-color: transparent;
}
@media (hover: hover) {
  :host([appearance="plain"]) .button:not(.disabled):not(.loading):hover {
    color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
    background-color: var(--wa-color-fill-quiet, var(--wa-color-neutral-fill-quiet));
  }
}
:host([appearance="plain"]) .button:not(.disabled):not(.loading):active {
  color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
  background-color: color-mix(in oklab, var(--wa-color-fill-quiet, var(--wa-color-neutral-fill-quiet)), var(--wa-color-mix-active));
}
:host([appearance="outlined"]) {
  margin-inline-start: var(--_button-horizontal-indent-outlined);
  margin-block-start: var(--_button-vertical-indent-outlined);
}
:host([appearance="outlined"]) .button {
  color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
  background-color: transparent;
  border-color: var(--wa-color-border-loud, var(--wa-color-neutral-border-loud));
}
@media (hover: hover) {
  :host([appearance="outlined"]) .button:not(.disabled):not(.loading):hover {
    color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
    background-color: var(--wa-color-fill-quiet, var(--wa-color-neutral-fill-quiet));
  }
}
:host([appearance="outlined"]) .button:not(.disabled):not(.loading):active {
  color: var(--wa-color-on-quiet, var(--wa-color-neutral-on-quiet));
  background-color: color-mix(in oklab, var(--wa-color-fill-quiet, var(--wa-color-neutral-fill-quiet)), var(--wa-color-mix-active));
}
:host([appearance="filled"]) {
  margin-inline-start: var(--_button-horizontal-indent);
  margin-block-start: var(--_button-vertical-indent);
}
:host([appearance="filled"]) .button {
  color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
  background-color: var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal));
  border-color: transparent;
}
@media (hover: hover) {
  :host([appearance="filled"]) .button:not(.disabled):not(.loading):hover {
    color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
    background-color: color-mix(in oklab, var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal)), var(--wa-color-mix-hover));
  }
}
:host([appearance="filled"]) .button:not(.disabled):not(.loading):active {
  color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
  background-color: color-mix(in oklab, var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal)), var(--wa-color-mix-active));
}
:host([appearance="filled-outlined"]) {
  margin-inline-start: var(--_button-horizontal-indent-outlined);
  margin-block-start: var(--_button-vertical-indent-outlined);
}
:host([appearance="filled-outlined"]) .button {
  color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
  background-color: var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal));
  border-color: var(--wa-color-border-normal, var(--wa-color-neutral-border-normal));
}
@media (hover: hover) {
  :host([appearance="filled-outlined"]) .button:not(.disabled):not(.loading):hover {
    color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
    background-color: color-mix(in oklab, var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal)), var(--wa-color-mix-hover));
  }
}
:host([appearance="filled-outlined"]) .button:not(.disabled):not(.loading):active {
  color: var(--wa-color-on-normal, var(--wa-color-neutral-on-normal));
  background-color: color-mix(in oklab, var(--wa-color-fill-normal, var(--wa-color-neutral-fill-normal)), var(--wa-color-mix-active));
}
:host([appearance="accent"]) {
  margin-inline-start: var(--_button-horizontal-indent);
  margin-block-start: var(--_button-vertical-indent);
}
:host([appearance="accent"]) .button {
  color: var(--wa-color-on-loud, var(--wa-color-neutral-on-loud));
  background-color: var(--wa-color-fill-loud, var(--wa-color-neutral-fill-loud));
  border-color: transparent;
}
@media (hover: hover) {
  :host([appearance="accent"]) .button:not(.disabled):not(.loading):hover {
    background-color: color-mix(in oklab, var(--wa-color-fill-loud, var(--wa-color-neutral-fill-loud)), var(--wa-color-mix-hover));
  }
}
:host([appearance="accent"]) .button:not(.disabled):not(.loading):active {
  background-color: color-mix(in oklab, var(--wa-color-fill-loud, var(--wa-color-neutral-fill-loud)), var(--wa-color-mix-active));
}
.button:focus {
  outline: none;
}
.button:focus-visible {
  outline: var(--wa-focus-ring);
  outline-offset: var(--wa-focus-ring-offset);
}
:host([disabled]) {
  opacity: 0.5;
  cursor: not-allowed;
}
:host([disabled]) .button {
  pointer-events: none;
}
.button::-moz-focus-inner {
  border: 0;
}
.button.is-icon-button {
  outline-offset: 2px;
  width: var(--wa-form-control-height);
  aspect-ratio: 1;
}
.button.is-icon-button.caret {
  width: auto;
  aspect-ratio: auto;
  min-width: var(--wa-form-control-height);
}
:host([pill]) .button {
  border-start-start-radius: var(--_button-start-start-radius, var(--wa-border-radius-pill));
  border-start-end-radius: var(--_button-start-end-radius, var(--wa-border-radius-pill));
  border-end-start-radius: var(--_button-end-start-radius, var(--wa-border-radius-pill));
  border-end-end-radius: var(--_button-end-end-radius, var(--wa-border-radius-pill));
}
.start,
.end {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  pointer-events: none;
}
.label {
  display: inline-block;
}
.is-icon-button .label {
  display: flex;
  justify-content: center;
}
.label::slotted(wa-icon) {
  align-self: center;
}
wa-icon[part=caret] {
  display: flex;
  align-self: center;
  align-items: center;
}
wa-icon[part=caret]::part(svg) {
  width: 0.875em;
  height: 0.875em;
}
.button:has(wa-icon[part=caret]) .end {
  display: none;
}
.loading {
  position: relative;
  cursor: wait;
}
.loading .start,
.loading .label,
.loading .end,
.loading .caret {
  opacity: 0;
  pointer-events: none;
}
.loading wa-spinner {
  --indicator-color: currentColor;
  --track-color: color-mix(in oklab, currentColor, transparent 90%);
  position: absolute;
  font-size: 1em;
  height: 1em;
  width: 1em;
  top: calc(50% - 0.5em);
  left: calc(50% - 0.5em);
}
.button ::slotted(wa-badge) {
  border-color: var(--wa-color-surface-default);
  position: absolute;
  inset-block-start: 0;
  inset-inline-end: 0;
  translate: 50% -50%;
  pointer-events: none;
}
:host(:dir(rtl)) ::slotted(wa-badge) {
  translate: -50% -50%;
}
slot[name=start]::slotted(*) {
  margin-inline-end: 0.75em;
}
slot[name=end]::slotted(*),
.button:not(.visually-hidden-label) [part=caret] {
  margin-inline-start: 0.75em;
}
`;var Go=Object.defineProperty,Jo=Object.getOwnPropertyDescriptor,u=(o,t,e,i)=>{for(var a=i>1?void 0:i?Jo(t,e):t,r=o.length-1,n;r>=0;r--)(n=o[r])&&(a=(i?n(t,e,a):n(a))||a);return i&&a&&Go(t,e,a),a},h=class extends ${constructor(){super(...arguments),this.assumeInteractionOn=["click"],this.hasSlotController=new H(this,"[default]","start","end"),this.localize=new X(this),this.invalid=!1,this.isIconButton=!1,this.title="",this.accessibleLabel="",this.ariaLabel=null,this.variant="neutral",this.appearance="accent",this.size="m",this.withCaret=!1,this.withStart=!1,this.withEnd=!1,this.disabled=!1,this.loading=!1,this.pill=!1,this.type="button",this.iconTag="wa-icon"}static get validators(){return[...super.validators,Oe()]}handleSizeChange(){Be(this.localName,this.size)}constructLightDOMButton(){let o=document.createElement("button");for(let t of this.attributes)t.name!=="style"&&o.setAttribute(t.name,t.value);return o.type=this.type,o.style.position="absolute !important",o.style.width="0 !important",o.style.height="0 !important",o.style.clipPath="inset(50%) !important",o.style.overflow="hidden !important",o.style.whiteSpace="nowrap !important",this.name&&(o.name=this.name),o.value=this.value||"",o}handleClick(o){if(this.disabled||this.loading){o.preventDefault(),o.stopImmediatePropagation();return}if(this.type!=="submit"&&this.type!=="reset"||!this.getForm())return;let e=this.constructLightDOMButton();this.parentElement?.append(e),e.click(),e.remove()}handleInvalid(){this.dispatchEvent(new V)}handleLabelSlotChange(){let o=this.labelSlot.assignedNodes({flatten:!0}),t=!1,e=!1,i=!1,a=!1,r=this.iconTag==="wa-icon";[...o].forEach(n=>{if(n.nodeType===Node.ELEMENT_NODE){let l=n;n.localName===this.iconTag&&(e=!0,t||(t=n.hasAttribute(r?"label":"aria-label"))),l.localName==="wa-icon"?(e=!0,t||(t=l.label!==void 0)):a=!0}else n.nodeType===Node.TEXT_NODE&&(n.textContent?.trim()||"").length>0&&(i=!0)}),this.isIconButton=e&&!i&&!a,this.customStates.set("icon-button",this.isIconButton),this.isIconButton&&!t&&!this.accessibleLabel&&!this.ariaLabel&&console.warn(`Icon buttons must have a label for screen readers. Add <${this.iconTag} ${r?"label":"aria-label"}="..."> to remove this warning.`,this)}isButton(){return!this.href}isLink(){return!!this.href}handleDisabledChange(){this.customStates.set("disabled",this.disabled),this.updateValidity()}handleHrefChange(){this.customStates.set("link",this.isLink())}handleLoadingChange(){this.customStates.set("loading",this.loading)}setValue(...o){}click(){this.button.click()}focus(o){this.button.focus(o)}blur(){this.button.blur()}render(){let o=this.isLink(),t=o?Nt`a`:Nt`button`;return bt`
      <${t}
        part="base button"
        class=${ot({button:!0,caret:this.withCaret,disabled:this.disabled,loading:this.loading,rtl:this.localize.dir()==="rtl","has-label":this.hasSlotController.test("[default]"),"has-start":this.hasSlotController.test("start","withStart"),"has-end":this.hasSlotController.test("end","withEnd"),"is-icon-button":this.isIconButton})}
        ?disabled=${L(o?void 0:this.disabled)}
        type=${L(o?void 0:this.type)}
        title=${this.title}
        name=${L(o?void 0:this.name)}
        value=${L(o?void 0:this.value)}
        href=${L(o?this.href:void 0)}
        target=${L(o?this.target:void 0)}
        download=${L(o?this.download:void 0)}
        rel=${L(o&&this.rel?this.rel:void 0)}
        role=${L(o?void 0:"button")}
        aria-disabled=${L(o&&this.disabled?"true":void 0)}
        aria-label=${L(this.accessibleLabel||this.ariaLabel||void 0)}
        aria-busy=${this.loading?"true":"false"}
        tabindex=${this.disabled?"-1":"0"}
        @invalid=${this.isButton()?this.handleInvalid:null}
        @click=${this.handleClick}
      >
        <slot name="start" part="start" class="start"></slot>
        <slot part="label" class="label" @slotchange=${this.handleLabelSlotChange}></slot>
        <slot name="end" part="end" class="end"></slot>
        ${this.withCaret?bt`
                <wa-icon part="caret" class="caret" library="system" name="chevron-down" variant="solid"></wa-icon>
              `:""}
        ${this.loading?bt`<wa-spinner part="spinner"></wa-spinner>`:""}
      </${t}>
    `}};h.shadowRootOptions={...$.shadowRootOptions,delegatesFocus:!0};h.css=[so,je,xt];u([Ot(".button")],h.prototype,"button",2);u([Ot("slot:not([name])")],h.prototype,"labelSlot",2);u([et()],h.prototype,"invalid",2);u([et()],h.prototype,"isIconButton",2);u([c()],h.prototype,"title",2);u([c({attribute:"accessible-label"})],h.prototype,"accessibleLabel",2);u([c({attribute:"aria-label"})],h.prototype,"ariaLabel",2);u([c({reflect:!0})],h.prototype,"variant",2);u([c({reflect:!0})],h.prototype,"appearance",2);u([c({reflect:!0})],h.prototype,"size",2);u([F("size")],h.prototype,"handleSizeChange",1);u([c({attribute:"with-caret",type:Boolean,reflect:!0})],h.prototype,"withCaret",2);u([c({attribute:"with-start",type:Boolean})],h.prototype,"withStart",2);u([c({attribute:"with-end",type:Boolean})],h.prototype,"withEnd",2);u([c({type:Boolean})],h.prototype,"disabled",2);u([c({type:Boolean,reflect:!0})],h.prototype,"loading",2);u([c({type:Boolean,reflect:!0})],h.prototype,"pill",2);u([c()],h.prototype,"type",2);u([c({reflect:!0})],h.prototype,"name",2);u([c({reflect:!0})],h.prototype,"value",2);u([c({reflect:!0})],h.prototype,"href",2);u([c()],h.prototype,"target",2);u([c()],h.prototype,"rel",2);u([c()],h.prototype,"download",2);u([c({attribute:"formaction"})],h.prototype,"formAction",2);u([c({attribute:"formenctype"})],h.prototype,"formEnctype",2);u([c({attribute:"formmethod"})],h.prototype,"formMethod",2);u([c({attribute:"formnovalidate",type:Boolean})],h.prototype,"formNoValidate",2);u([c({attribute:"formtarget"})],h.prototype,"formTarget",2);u([c()],h.prototype,"iconTag",2);u([F("disabled",{waitUntilFirstUpdate:!0})],h.prototype,"handleDisabledChange",1);u([F("href")],h.prototype,"handleHrefChange",1);u([F("loading",{waitUntilFirstUpdate:!0})],h.prototype,"handleLoadingChange",1);h=u([k("wa-button")],h);h.disableWarning?.("change-in-update");var Jt=class extends h{constructor(){super(...arguments);this.appearance="outlined";this.pressed=void 0}static{this.properties={pressed:{type:Boolean}}}updated(e){super.updated(e),this.pressed===void 0?this.button.removeAttribute("aria-pressed"):this.button.setAttribute("aria-pressed",String(this.pressed))}static get styles(){return[h.styles,v`
        :host {
          --wa-form-control-height: var(--axis-control-height);
          --wa-form-control-padding-inline: var(--axis-space-3);
          --wa-form-control-border-radius: var(--axis-radius-control);
          --wa-form-control-border-width: var(--axis-border-width);
          --wa-form-control-border-style: solid;
          --wa-font-weight-action: var(--axis-font-weight-medium);
          --wa-button-transform-hover: none;
          --wa-button-transform-active: none;
        }
        .button {
          min-block-size: var(--axis-control-height);
          block-size: auto;
          padding-block: var(--axis-space-2);
          white-space: normal;
          overflow-wrap: anywhere;
        }
      `]}};customElements.define("axis-button",Jt);var lo=v`:host {
  --spacing: var(--wa-space-l);
  --inner-border-radius: calc(var(--wa-panel-border-radius) - var(--wa-panel-border-width));
  display: flex;
  flex-direction: column;
  background-color: var(--wa-color-surface-default);
  border-color: var(--wa-color-surface-border);
  border-radius: var(--wa-panel-border-radius);
  border-style: var(--wa-panel-border-style);
  box-shadow: var(--wa-shadow-s);
  border-width: var(--wa-panel-border-width);
  color: var(--wa-color-text-normal);
}
:host([appearance="plain"]) {
  background-color: transparent;
  border-color: transparent;
  box-shadow: none;
}
:host([appearance="outlined"]) {
  background-color: var(--wa-color-surface-default);
  border-color: var(--wa-color-surface-border);
}
:host([appearance="filled"]) {
  background-color: var(--wa-color-neutral-fill-quiet);
  border-color: transparent;
}
:host([appearance="filled-outlined"]) {
  background-color: var(--wa-color-neutral-fill-quiet);
  border-color: var(--wa-color-surface-border);
}
:host([appearance="accent"]) {
  color: var(--wa-color-neutral-on-loud);
  background-color: var(--wa-color-neutral-fill-loud);
  border-color: transparent;
}
.media,
:host(:not([with-media])) .header,
:host(:not([with-media], [with-header])) .body {
  border-start-start-radius: var(--inner-border-radius);
  border-start-end-radius: var(--inner-border-radius);
}
:host(:not([with-footer])) .body,
.footer {
  border-end-start-radius: var(--inner-border-radius);
  border-end-end-radius: var(--inner-border-radius);
}
.media {
  display: flex;
  overflow: hidden;
}
.media::slotted(*) {
  display: block;
  width: 100%;
  border-radius: 0 !important;
}
:host([appearance="plain"]) .media {
  border-radius: var(--inner-border-radius);
}
:host([appearance="plain"]) .media::slotted(*) {
  border-radius: inherit !important;
}
.header {
  display: block;
  border-block-end-style: inherit;
  border-block-end-color: var(--wa-color-surface-border);
  border-block-end-width: var(--wa-panel-border-width);
  padding: calc(var(--spacing) / 2) var(--spacing);
}
.body {
  display: block;
  padding: var(--spacing);
}
.footer {
  display: block;
  border-block-start-style: inherit;
  border-block-start-color: var(--wa-color-surface-border);
  border-block-start-width: var(--wa-panel-border-width);
  padding: var(--spacing);
}
.has-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
:host(:not([with-header])) .header,
:host(:not([with-footer])) .footer,
:host(:not([with-media])) .media {
  display: none;
}
:host([orientation="horizontal"]) {
  flex-direction: row;
}
:host([orientation="horizontal"]) .media {
  border-start-start-radius: var(--inner-border-radius);
  border-end-start-radius: var(--inner-border-radius);
  border-start-end-radius: 0;
}
:host([orientation="horizontal"]) .media::slotted(*) {
  block-size: 100%;
  inline-size: 100%;
  object-fit: cover;
}
:host([orientation="horizontal"]) .body slot::slotted(*) {
  display: block;
  height: 100%;
  margin: 0;
}
:host([orientation="horizontal"]) slot[name=actions]::slotted(*) {
  display: flex;
  align-items: center;
  padding: var(--spacing);
}
`;var Zo=Object.defineProperty,Qo=Object.getOwnPropertyDescriptor,I=(o,t,e,i)=>{for(var a=i>1?void 0:i?Qo(t,e):t,r=o.length-1,n;r>=0;r--)(n=o[r])&&(a=(i?n(t,e,a):n(a))||a);return i&&a&&Zo(t,e,a),a},C=class extends x{constructor(){super(...arguments),this.hasSlotController=new H(this,"footer","header","media","header-actions","footer-actions","actions"),this.appearance="outlined",this.withHeader=!1,this.withMedia=!1,this.withFooter=!1,this.withHeaderActions=!1,this.withFooterActions=!1,this.orientation="vertical"}willUpdate(o){this.withHeader=this.hasSlotController.test("header","withHeader"),this.withMedia=this.hasSlotController.test("media","withMedia"),this.withFooter=this.hasSlotController.test("footer","withFooter"),super.willUpdate(o)}render(){if(this.orientation==="horizontal")return p`
        <slot name="media" part="media" class="media"></slot>
        <div part="body" class="body"><slot></slot></div>
        <slot name="actions" part="actions" class="actions"></slot>
      `;let o=this.hasSlotController.test("header-actions","withHeaderActions"),t=this.hasSlotController.test("footer-actions","withFooterActions");return p`
      <slot name="media" part="media" class="media"></slot>

      <div
        part="header"
        class=${ot({header:!0,"has-actions":o})}
      >
        <slot name="header"></slot>
        <slot name="header-actions"></slot>
      </div>

      <div part="body" class="body"><slot></slot></div>

      <div
        part="footer"
        class=${ot({footer:!0,"has-actions":t})}
      >
        <slot name="footer"></slot>
        <slot name="footer-actions"></slot>
      </div>
    `}};C.css=[xt,lo];I([c({reflect:!0})],C.prototype,"appearance",2);I([c({attribute:"with-header",type:Boolean,reflect:!0})],C.prototype,"withHeader",2);I([c({attribute:"with-media",type:Boolean,reflect:!0})],C.prototype,"withMedia",2);I([c({attribute:"with-footer",type:Boolean,reflect:!0})],C.prototype,"withFooter",2);I([c({attribute:"with-header-actions",type:Boolean,reflect:!0})],C.prototype,"withHeaderActions",2);I([c({attribute:"with-footer-actions",type:Boolean,reflect:!0})],C.prototype,"withFooterActions",2);I([c({reflect:!0})],C.prototype,"orientation",2);C=I([k("wa-card")],C);C.disableWarning?.("change-in-update");var Zt=class extends C{static get styles(){return[C.styles,v`
        :host {
          --spacing: var(--axis-space-4);
          --wa-panel-border-radius: var(--axis-radius-card);
          --wa-panel-border-width: var(--axis-border-width);
          --wa-panel-border-style: solid;
          --wa-shadow-s: none;
          min-inline-size: 0;
        }
      `]}};customElements.define("axis-card",Zt);function _t(o){return o.alias.trim()||o.discovery?.name.trim()||o.model.trim()||o.serial}var Qt=class extends y{constructor(){super(...arguments);this.device=null;this.health=null;this.loading=!1;this.connected=!1}static{this.properties={device:{attribute:!1},health:{attribute:!1},loading:{type:Boolean},connected:{type:Boolean}}}static{this.styles=U}render(){if(!this.device)return m;let e=this.health?.serial===this.device.serial;return p`
      <axis-card>
        <h2>${_t(this.device)}</h2>
        <axis-button
          ?disabled=${this.loading||!this.connected}
          @click=${()=>this.dispatchEvent(new Event("axis-refresh"))}
          >Refresh health</axis-button
        >
        ${this.loading?p`<p role="status">Contacting the device. This may take up to 60 seconds.</p>`:m}
        ${!this.loading&&!this.health?p`<p>No live health data available. Check the connection and use Refresh health to try again.</p>`:m}
        ${this.health?p`
                ${e?m:p`<p class="warning">Warning: the connected device serial does not match the saved target.</p>`}
                <dl>
                  ${e?p`<dt>Serial</dt>
                          <dd>${this.health.serial}</dd>`:p`<dt>Saved serial</dt>
                          <dd>${this.device.serial}</dd>
                          <dt>Reported serial</dt>
                          <dd>${this.health.serial}</dd>`}
                  <dt>Product</dt>
                  <dd>${this.health.product}</dd>
                  <dt>Model</dt>
                  <dd>${this.health.model}</dd>
                  <dt>Firmware</dt>
                  <dd>${this.health.firmware_version}</dd>
                  <dt>Read at</dt>
                  <dd>${this.health.observed_at}</dd>
                </dl>
              `:m}
      </axis-card>
    `}};customElements.define("axis-device-health",Qt);function Et(o){let t=o?.trim().toLowerCase().replace(/\*+$/,"").replace(/[:-]/g,"");return t&&/^[0-9a-f]{12}$/.test(t)?t:void 0}function co(o,t,e,i){return[o?`${o} (${t})`:t,e,i].filter(Boolean).join(" \u2014 ")}function ti(o,t){let e=Et(o.macaddress);return t.some(i=>i.serial===o.serial||e!==void 0&&(e===Et(i.serial)||e===Et(i.discovery?.macaddress)))}var te=class extends y{constructor(){super(...arguments);this.devices=[];this.discovery=null;this.selected="";this.connected=!1}static{this.properties={devices:{attribute:!1},discovery:{attribute:!1},selected:{},connected:{type:Boolean}}}static{this.styles=[U,v`
      .device-rows {
        display: grid;
        gap: var(--axis-space-2);
        list-style: none;
        margin-block: var(--axis-space-2) 0;
        padding: 0;
      }
      .device-rows li {
        min-inline-size: 0;
      }
      .device-rows axis-button {
        display: block;
        inline-size: 100%;
      }
      .device-rows axis-button::part(base) {
        justify-content: flex-start;
        text-align: start;
      }
      .discovered {
        --wa-color-neutral-border-quiet: var(--axis-color-warning);
      }
      .discovered::part(base) {
        border-color: var(--axis-color-warning);
      }
      .scan-control {
        position: relative;
        display: inline-flex;
      }
      .scan-control .scanning::part(base) {
        border-color: transparent;
      }
      .scan-control .failed::part(base) {
        border-color: var(--axis-color-danger);
      }
      .scan-outline {
        position: absolute;
        inset: 0;
        inline-size: 100%;
        block-size: 100%;
        pointer-events: none;
      }
      .scan-outline rect {
        x: 1px;
        y: 1px;
        width: calc(100% - 2px);
        height: calc(100% - 2px);
        rx: var(--axis-radius-control);
        fill: none;
        stroke: var(--axis-color-primary);
        stroke-width: 2px;
        stroke-dasharray: 3 2;
        animation: scan-dashes 650ms linear infinite;
      }
      @keyframes scan-dashes {
        to {
          stroke-dashoffset: -5;
        }
      }
      @media (prefers-reduced-motion: reduce) {
        .scan-outline rect {
          animation: none;
        }
      }
      .scan-status {
        position: absolute;
        inline-size: 1px;
        block-size: 1px;
        overflow: hidden;
        clip-path: inset(50%);
        white-space: nowrap;
      }
    `]}render(){let e=this.discovery,i=e&&e.status!=="error"?e.devices:[],a=i.filter(d=>!ti(d,this.devices)),r=e?.status==="scanning",n=e?.status==="error",l=r?"Scanning\u2026":n?"Retry scan \xB7 Scan failed":e?.status==="complete"?`Scan again \xB7 ${a.length?`${a.length} new`:"No new devices"}`:"Scan local network",s=n?e.message:e?.status==="complete"&&!a.length?i.length?"All discovered devices are already saved.":"No Axis devices found.":e?l:"";return p`
      <axis-card>
        <h2>Devices</h2>
        <p>
          Saved details are not a live health check. Discovered devices are
          unverified; select one to save it.
        </p>
        <div class="actions">
          <axis-button
            ?disabled=${!this.connected}
            @click=${()=>this.dispatchEvent(new Event("axis-refresh"))}
            >Refresh list</axis-button
          >
          <span class="scan-control">
            <axis-button
              class=${r?"scanning":n?"failed":""}
              ?disabled=${!this.connected}
              aria-disabled=${r?"true":"false"}
              title=${n?e.message:""}
              @click=${()=>{this.connected&&!r&&this.dispatchEvent(new Event("axis-scan"))}}
              >${l}</axis-button
            >
            ${r?p`<svg class="scan-outline" aria-hidden="true">
                    <rect pathLength="100"></rect>
                  </svg>`:m}
            <span class="scan-status" role="status">${s}</span>
          </span>
        </div>
        ${this.devices.length===0?p`<p>No saved devices. Scan the local network to find devices to save.</p>`:""}
        ${this.devices.length||a.length?p`
                <ul class="device-rows" role="list" aria-label="Devices">
                  ${this.devices.map(d=>p`
                      <li>
                        <axis-button
                          variant=${d.serial===this.selected?"brand":"neutral"}
                          appearance=${d.serial===this.selected?"accent":"outlined"}
                          .pressed=${d.serial===this.selected}
                          ?disabled=${!this.connected}
                          @click=${()=>this.dispatchEvent(new CustomEvent("axis-select",{detail:d.serial}))}
                        >
                          ${co(_t(d),d.host,d.discovery?.macaddress||Et(d.serial)?.match(/../g)?.join(":"))}
                        </axis-button>
                      </li>
                    `)}
                  ${a.map(d=>p`
                      <li>
                        <axis-button
                          class="discovered"
                          ?disabled=${!this.connected||r}
                          @click=${()=>this.dispatchEvent(new CustomEvent("axis-register",{detail:d}))}
                        >
                          ${co(d.name,d.host,d.macaddress,d.model)}
                          <span class="warning">· Discovered</span>
                        </axis-button>
                      </li>
                    `)}
                </ul>
              `:m}
      </axis-card>
    `}};customElements.define("axis-device-list",te);var ee=class extends y{constructor(){super(...arguments);this.status="Connecting";this.devices=[];this.discovery=null;this.selected="";this.health=null;this.interfaces=[];this.data=null;this.error="";this.loading=!1;this.registration=null;this.saving=!1;this.saveError="";this.operation=0;this.refreshId=0;this.connection=new wt(e=>this.connectionChanged(e));this.openAccessLink=()=>{let e=location.hash.slice(1)||sessionStorage.getItem("axis-token")||"";if(location.hash&&(sessionStorage.setItem("axis-token",e),history.replaceState(null,"",location.pathname)),!e){this.connection.disconnect(),this.status="Access link required",this.error="Open the private URL printed when the server starts.";return}this.connection.connect(e)}}static{this.properties={status:{state:!0},devices:{state:!0},discovery:{state:!0},selected:{state:!0},health:{state:!0},interfaces:{state:!0},data:{state:!0},error:{state:!0},loading:{state:!0},registration:{state:!0},saving:{state:!0},saveError:{state:!0}}}static{this.styles=[U,v`
      main {
        max-inline-size: var(--axis-content-width);
        margin-inline: auto;
        padding: var(--axis-space-6);
      }
      header {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: baseline;
        gap: var(--axis-space-4);
      }
      .panels {
        display: grid;
        gap: var(--axis-space-4);
      }
      .error {
        color: var(--axis-color-danger);
      }
      fieldset {
        display: grid;
        gap: var(--axis-space-3);
        border: 0;
        padding: 0;
        margin: 0;
        min-inline-size: 0;
      }
      label {
        display: grid;
        gap: var(--axis-space-1);
        max-inline-size: 28rem;
      }
      .certificate {
        display: block;
      }
      input,
      button {
        font: inherit;
        color: inherit;
      }
      input:not([type="checkbox"]),
      button {
        min-block-size: var(--axis-control-height);
        padding-inline: var(--axis-space-3);
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-control);
        background: var(--axis-color-surface);
      }
      button[type="submit"] {
        background: var(--axis-color-primary);
        color: var(--axis-color-on-primary);
      }
      .registration-target {
        overflow-wrap: anywhere;
      }
    `]}connectedCallback(){super.connectedCallback(),window.addEventListener("hashchange",this.openAccessLink),this.openAccessLink()}disconnectedCallback(){window.removeEventListener("hashchange",this.openAccessLink),this.connection.disconnect(),super.disconnectedCallback()}connectionChanged(e){if(this.status={connecting:"Connecting",connected:"Connected",disconnected:"Disconnected; reconnecting",denied:"Access denied"}[e],this.error=e==="denied"?"Open the private URL printed by the running server.":"",e==="connected"){this.refreshDevices();return}++this.operation,++this.refreshId,this.discovery=null,this.registration=null,this.saving=!1,this.saveError="",this.health=null,this.interfaces=[],this.data=null,this.loading=!1}async refreshDevices(){let e=++this.refreshId;try{let i=await Se(this.connection);if(this.refreshId!==e)return;this.devices=i,this.error="",this.selected&&this.devices.some(a=>a.serial===this.selected)?await this.selectDevice(this.selected):(++this.operation,this.selected="",this.loading=!1)}catch(i){this.refreshId===e&&(this.error=i.message)}}async scanLocalNetwork(){if(this.status!=="Connected"||this.saving||this.discovery?.status==="scanning")return;this.registration=null;let e={status:"scanning",devices:this.discovery?.status==="complete"?this.discovery.devices:[]};this.discovery=e;try{let i=await Ae(this.connection);this.discovery===e&&(this.discovery={status:"complete",devices:i})}catch(i){this.discovery===e&&(this.discovery={status:"error",message:i.message})}}openRegistration(e){this.registration=e,this.saveError="",this.selected="",++this.operation}async submitRegistration(e){e.preventDefault();let i=e.currentTarget,a=this.registration;if(!(i instanceof HTMLFormElement)||!a||this.saving)return;let r=new FormData(i),n=i.querySelector('input[name="password"]');n&&(n.value=""),this.saving=!0,this.saveError="";try{let l=await _e(this.connection,{host:a.host,username:String(r.get("username")??""),password:String(r.get("password")??""),alias:String(r.get("alias")??""),verify_ssl:!r.has("selfSigned")});if(this.registration!==a)return;this.registration=null,this.saving=!1,this.selected=l,await this.refreshDevices()}catch(l){this.registration===a&&(this.saveError=l.message)}finally{this.registration===a&&(this.saving=!1)}}renderRegistration(e){return ze(e.host,p`
        <axis-card>
          <h2>Save device</h2>
          <p class="registration-target">
            Connect over HTTPS to ${e.name||e.host}
            ${e.name?`(${e.host})`:""}.
          </p>
          <form method="post" @submit=${this.submitRegistration}>
            <fieldset ?disabled=${this.saving}>
              <label
                >Username
                <input name="username" autocomplete="username" required
              /></label>
              <label
                >Password
                <input
                  name="password"
                  type="password"
                  autocomplete="current-password"
                  required
              /></label>
              <label>Alias (optional) <input name="alias" /></label>
              <label class="certificate">
                <input name="selfSigned" type="checkbox" checked />
                Allow a self-signed certificate
              </label>
              <p class="warning">
                Allowing self-signed certificates skips server identity
                verification. Check the address and only continue if you trust
                this device and network.
              </p>
              <div class="actions">
                <button type="submit">Save device</button>
                <button
                  type="button"
                  @click=${()=>{this.registration=null}}
                >
                  Cancel
                </button>
              </div>
            </fieldset>
          </form>
          <div role="status">
            ${this.saving?"Verifying and saving device\u2026":m}
          </div>
          ${this.saveError?p`<p class="error" role="alert">${this.saveError}</p>`:m}
        </axis-card>
      `)}async selectDevice(e){let i=++this.operation;this.selected=e,this.health=null,this.interfaces=[],this.data=null,this.error="",this.loading=!0;try{let a=await Ee(this.connection,e);this.operation===i&&(this.health=a)}catch(a){this.operation===i&&(this.error=a.message)}finally{this.operation===i&&(this.loading=!1)}}async browse(e,i){let a=++this.operation;this.loading=!0,this.error="";try{let r=await e();if(this.operation!==a)return;i?.(r),this.data=r}catch(r){this.operation===a&&(this.error=r.message)}finally{this.operation===a&&(this.loading=!1)}}render(){let e=this.devices.find(a=>a.serial===this.selected),i=this.status==="Connected";return p`
      <main>
        <header>
          <h1>Axis devices</h1>
          <span role="status">${this.status}</span>
        </header>
        ${this.error?p`<p class="error" role="alert">${this.error}</p>`:m}
        <div class="panels">
          <axis-device-list
            .devices=${this.devices}
            .discovery=${this.discovery}
            .selected=${this.selected}
            .connected=${i&&!this.saving}
            @axis-refresh=${this.refreshDevices}
            @axis-scan=${this.scanLocalNetwork}
            @axis-select=${a=>{this.registration=null,this.selectDevice(a.detail)}}
            @axis-register=${a=>this.openRegistration(a.detail)}
          >
          </axis-device-list>
          ${this.registration?this.renderRegistration(this.registration):m}
          ${e?p`
                  <axis-device-health
                    .device=${e}
                    .health=${this.health}
                    .connected=${i}
                    .loading=${this.loading}
                    @axis-refresh=${()=>this.selectDevice(e.serial)}
                  >
                  </axis-device-health>
                  <axis-card>
                    <h2>APIs and interfaces</h2>
                    <div class="actions">
                      <axis-button
                        ?disabled=${this.loading||!i}
                        @click=${()=>this.browse(()=>Me(this.connection,e.serial))}
                        >List APIs</axis-button
                      >
                      <axis-button
                        ?disabled=${this.loading||!i}
                        @click=${()=>this.browse(()=>ke(this.connection,e.serial),a=>{this.interfaces=a})}
                        >Check interfaces</axis-button
                      >
                      ${this.interfaces.map(a=>p`
                          <axis-button
                            ?disabled=${this.loading||!i||!a.supported}
                            @click=${()=>this.browse(()=>Fe(this.connection,e.serial,a.name))}
                          >
                            ${a.name}
                          </axis-button>
                        `)}
                    </div>
                    ${this.data!==null?p`<pre>${JSON.stringify(this.data,null,2)}</pre>`:m}
                  </axis-card>
                `:m}
        </div>
      </main>
    `}};customElements.define("axis-app",ee);
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
lit-html/directive.js:
@lit/reactive-element/decorators/custom-element.js:
@lit/reactive-element/decorators/property.js:
@lit/reactive-element/decorators/state.js:
@lit/reactive-element/decorators/event-options.js:
@lit/reactive-element/decorators/base.js:
@lit/reactive-element/decorators/query.js:
@lit/reactive-element/decorators/query-all.js:
@lit/reactive-element/decorators/query-async.js:
@lit/reactive-element/decorators/query-assigned-nodes.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directive-helpers.js:
lit-html/static.js:
  (**
   * @license
   * Copyright 2020 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directives/keyed.js:
@lit/reactive-element/decorators/query-assigned-elements.js:
  (**
   * @license
   * Copyright 2021 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directives/class-map.js:
lit-html/directives/if-defined.js:
  (**
   * @license
   * Copyright 2018 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@home-assistant/webawesome/dist/events/invalid.js:
@home-assistant/webawesome/dist/internal/size.js:
@home-assistant/webawesome/dist/internal/slot.js:
@home-assistant/webawesome/dist/internal/validators/mirror-validator.js:
@home-assistant/webawesome/dist/internal/watch.js:
@home-assistant/webawesome/dist/internal/validators/custom-error-validator.js:
@home-assistant/webawesome/dist/styles/component/host.styles.js:
@home-assistant/webawesome/dist/utilities/polyfills/stateset.js:
@home-assistant/webawesome/dist/internal/webawesome-element.js:
@home-assistant/webawesome/dist/internal/webawesome-form-associated-element.js:
@home-assistant/webawesome/dist/styles/component/size.styles.js:
@home-assistant/webawesome/dist/styles/component/variants.styles.js:
@home-assistant/webawesome/dist/translations/en.js:
@home-assistant/webawesome/dist/utilities/localize.js:
@home-assistant/webawesome/dist/events/error.js:
@home-assistant/webawesome/dist/events/load.js:
@home-assistant/webawesome/dist/components/icon/icon.styles.js:
@home-assistant/webawesome/dist/utilities/base-path.js:
@home-assistant/webawesome/dist/components/icon/library.default.js:
@home-assistant/webawesome/dist/components/icon/library.system.js:
@home-assistant/webawesome/dist/components/icon/library.js:
@home-assistant/webawesome/dist/components/icon/icon.js:
@home-assistant/webawesome/dist/components/spinner/spinner.styles.js:
@home-assistant/webawesome/dist/components/spinner/spinner.js:
@home-assistant/webawesome/dist/components/button/button.styles.js:
@home-assistant/webawesome/dist/components/button/button.js:
@home-assistant/webawesome/dist/components/card/card.styles.js:
@home-assistant/webawesome/dist/components/card/card.js:
  (*! Copyright 2026 Fonticons, Inc. - https://webawesome.com/license *)
*/
