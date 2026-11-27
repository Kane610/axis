var de=globalThis,pe=de.ShadowRoot&&(de.ShadyCSS===void 0||de.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Me=Symbol(),ct=new WeakMap,G=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==Me)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(pe&&t===void 0){let i=e!==void 0&&e.length===1;i&&(t=ct.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&ct.set(e,t))}return t}toString(){return this.cssText}},dt=n=>new G(typeof n=="string"?n:n+"",void 0,Me),v=(n,...t)=>{let e=n.length===1?n[0]:t.reduce((i,a,s)=>i+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(a)+n[s+1],n[0]);return new G(e,n,Me)},pt=(n,t)=>{if(pe)n.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let i=document.createElement("style"),a=de.litNonce;a!==void 0&&i.setAttribute("nonce",a),i.textContent=e.cssText,n.appendChild(i)}},Fe=pe?n=>n:n=>n instanceof CSSStyleSheet?(t=>{let e="";for(let i of t.cssRules)e+=i.cssText;return dt(e)})(n):n;var{is:Ri,defineProperty:Ti,getOwnPropertyDescriptor:Ii,getOwnPropertyNames:Oi,getOwnPropertySymbols:Ui,getPrototypeOf:qi}=Object,he=globalThis,ht=he.trustedTypes,Bi=ht?ht.emptyScript:"",Vi=he.reactiveElementPolyfillSupport,Z=(n,t)=>n,Q={toAttribute(n,t){switch(t){case Boolean:n=n?Bi:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,t){let e=n;switch(t){case Boolean:e=n!==null;break;case Number:e=n===null?null:Number(n);break;case Object:case Array:try{e=JSON.parse(n)}catch{e=null}}return e}},ue=(n,t)=>!Ri(n,t),ut={attribute:!0,type:String,converter:Q,reflect:!1,useDefault:!1,hasChanged:ue};Symbol.metadata??=Symbol("metadata"),he.litPropertyMetadata??=new WeakMap;var E=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ut){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let i=Symbol(),a=this.getPropertyDescriptor(t,i,e);a!==void 0&&Ti(this.prototype,t,a)}}static getPropertyDescriptor(t,e,i){let{get:a,set:s}=Ii(this.prototype,t)??{get(){return this[e]},set(o){this[e]=o}};return{get:a,set(o){let r=a?.call(this);s?.call(this,o),this.requestUpdate(t,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ut}static _$Ei(){if(this.hasOwnProperty(Z("elementProperties")))return;let t=qi(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(Z("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(Z("properties"))){let e=this.properties,i=[...Oi(e),...Ui(e)];for(let a of i)this.createProperty(a,e[a])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[i,a]of e)this.elementProperties.set(i,a)}this._$Eh=new Map;for(let[e,i]of this.elementProperties){let a=this._$Eu(e,i);a!==void 0&&this._$Eh.set(a,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let i=new Set(t.flat(1/0).reverse());for(let a of i)e.unshift(Fe(a))}else t!==void 0&&e.push(Fe(t));return e}static _$Eu(t,e){let i=e.attribute;return i===!1?void 0:typeof i=="string"?i:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return pt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){let i=this.constructor.elementProperties.get(t),a=this.constructor._$Eu(t,i);if(a!==void 0&&i.reflect===!0){let s=(i.converter?.toAttribute!==void 0?i.converter:Q).toAttribute(e,i.type);this._$Em=t,s==null?this.removeAttribute(a):this.setAttribute(a,s),this._$Em=null}}_$AK(t,e){let i=this.constructor,a=i._$Eh.get(t);if(a!==void 0&&this._$Em!==a){let s=i.getPropertyOptions(a),o=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:Q;this._$Em=a;let r=o.fromAttribute(e,s.type);this[a]=r??this._$Ej?.get(a)??r,this._$Em=null}}requestUpdate(t,e,i,a=!1,s){if(t!==void 0){let o=this.constructor;if(a===!1&&(s=this[t]),i??=o.getPropertyOptions(t),!((i.hasChanged??ue)(s,e)||i.useDefault&&i.reflect&&s===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,i))))return;this.C(t,e,i)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:a,wrapped:s},o){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,o??e??this[t]),s!==!0||o!==void 0)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),a===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[a,s]of this._$Ep)this[a]=s;this._$Ep=void 0}let i=this.constructor.elementProperties;if(i.size>0)for(let[a,s]of i){let{wrapped:o}=s,r=this[a];o!==!0||this._$AL.has(a)||r===void 0||this.C(a,void 0,s,r)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(i=>i.hostUpdate?.()),this.update(e)):this._$EM()}catch(i){throw t=!1,this._$EM(),i}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};E.elementStyles=[],E.shadowRootOptions={mode:"open"},E[Z("elementProperties")]=new Map,E[Z("finalized")]=new Map,Vi?.({ReactiveElement:E}),(he.reactiveElementVersions??=[]).push("2.1.2");var Te=globalThis,mt=n=>n,me=Te.trustedTypes,gt=me?me.createPolicy("lit-html",{createHTML:n=>n}):void 0,Ie="$lit$",_=`lit$${Math.random().toFixed(9).slice(2)}$`,Oe="?"+_,Ni=`<${Oe}>`,I=document,te=()=>I.createComment(""),ie=n=>n===null||typeof n!="object"&&typeof n!="function",Ue=Array.isArray,Ct=n=>Ue(n)||typeof n?.[Symbol.iterator]=="function",Re=`[ 	
\f\r]`,ee=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ft=/-->/g,vt=/>/g,R=RegExp(`>|${Re}(?:([^\\s"'>=/]+)(${Re}*=${Re}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),wt=/'/g,bt=/"/g,xt=/^(?:script|style|textarea|title)$/i,qe=n=>(t,...e)=>({_$litType$:n,strings:t,values:e}),c=qe(1),$t=qe(2),At=qe(3),P=Symbol.for("lit-noChange"),p=Symbol.for("lit-nothing"),yt=new WeakMap,T=I.createTreeWalker(I,129);function St(n,t){if(!Ue(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return gt!==void 0?gt.createHTML(t):t}var Lt=(n,t)=>{let e=n.length-1,i=[],a,s=t===2?"<svg>":t===3?"<math>":"",o=ee;for(let r=0;r<e;r++){let l=n[r],d,u,g=-1,y=0;for(;y<l.length&&(o.lastIndex=y,u=o.exec(l),u!==null);)y=o.lastIndex,o===ee?u[1]==="!--"?o=ft:u[1]!==void 0?o=vt:u[2]!==void 0?(xt.test(u[2])&&(a=RegExp("</"+u[2],"g")),o=R):u[3]!==void 0&&(o=R):o===R?u[0]===">"?(o=a??ee,g=-1):u[1]===void 0?g=-2:(g=o.lastIndex-u[2].length,d=u[1],o=u[3]===void 0?R:u[3]==='"'?bt:wt):o===bt||o===wt?o=R:o===ft||o===vt?o=ee:(o=R,a=void 0);let k=o===R&&n[r+1].startsWith("/>")?" ":"";s+=o===ee?l+Ni:g>=0?(i.push(d),l.slice(0,g)+Ie+l.slice(g)+_+k):l+_+(g===-2?r:k)}return[St(n,s+(n[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),i]},ae=class n{constructor({strings:t,_$litType$:e},i){let a;this.parts=[];let s=0,o=0,r=t.length-1,l=this.parts,[d,u]=Lt(t,e);if(this.el=n.createElement(d,i),T.currentNode=this.el.content,e===2||e===3){let g=this.el.content.firstChild;g.replaceWith(...g.childNodes)}for(;(a=T.nextNode())!==null&&l.length<r;){if(a.nodeType===1){if(a.hasAttributes())for(let g of a.getAttributeNames())if(g.endsWith(Ie)){let y=u[o++],k=a.getAttribute(g).split(_),C=/([.?@])?(.*)/.exec(y);l.push({type:1,index:s,name:C[2],strings:k,ctor:C[1]==="."?fe:C[1]==="?"?ve:C[1]==="@"?we:U}),a.removeAttribute(g)}else g.startsWith(_)&&(l.push({type:6,index:s}),a.removeAttribute(g));if(xt.test(a.tagName)){let g=a.textContent.split(_),y=g.length-1;if(y>0){a.textContent=me?me.emptyScript:"";for(let k=0;k<y;k++)a.append(g[k],te()),T.nextNode(),l.push({type:2,index:++s});a.append(g[y],te())}}}else if(a.nodeType===8)if(a.data===Oe)l.push({type:2,index:s});else{let g=-1;for(;(g=a.data.indexOf(_,g+1))!==-1;)l.push({type:7,index:s}),g+=_.length-1}s++}}static createElement(t,e){let i=I.createElement("template");return i.innerHTML=t,i}};function O(n,t,e=n,i){if(t===P)return t;let a=i!==void 0?e._$Co?.[i]:e._$Cl,s=ie(t)?void 0:t._$litDirective$;return a?.constructor!==s&&(a?._$AO?.(!1),s===void 0?a=void 0:(a=new s(n),a._$AT(n,e,i)),i!==void 0?(e._$Co??=[])[i]=a:e._$Cl=a),a!==void 0&&(t=O(n,a._$AS(n,t.values),a,i)),t}var ge=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:i}=this._$AD,a=(t?.creationScope??I).importNode(e,!0);T.currentNode=a;let s=T.nextNode(),o=0,r=0,l=i[0];for(;l!==void 0;){if(o===l.index){let d;l.type===2?d=new V(s,s.nextSibling,this,t):l.type===1?d=new l.ctor(s,l.name,l.strings,this,t):l.type===6&&(d=new be(s,this,t)),this._$AV.push(d),l=i[++r]}o!==l?.index&&(s=T.nextNode(),o++)}return T.currentNode=I,a}p(t){let e=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},V=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,a){this.type=2,this._$AH=p,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=a,this._$Cv=a?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=O(this,t,e),ie(t)?t===p||t==null||t===""?(this._$AH!==p&&this._$AR(),this._$AH=p):t!==this._$AH&&t!==P&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Ct(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==p&&ie(this._$AH)?this._$AA.nextSibling.data=t:this.T(I.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:i}=t,a=typeof i=="number"?this._$AC(t):(i.el===void 0&&(i.el=ae.createElement(St(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===a)this._$AH.p(e);else{let s=new ge(a,this),o=s.u(this.options);s.p(e),this.T(o),this._$AH=s}}_$AC(t){let e=yt.get(t.strings);return e===void 0&&yt.set(t.strings,e=new ae(t)),e}k(t){Ue(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,i,a=0;for(let s of t)a===e.length?e.push(i=new n(this.O(te()),this.O(te()),this,this.options)):i=e[a],i._$AI(s),a++;a<e.length&&(this._$AR(i&&i._$AB.nextSibling,a),e.length=a)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let i=mt(t).nextSibling;mt(t).remove(),t=i}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},U=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,a,s){this.type=1,this._$AH=p,this._$AN=void 0,this.element=t,this.name=e,this._$AM=a,this.options=s,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=p}_$AI(t,e=this,i,a){let s=this.strings,o=!1;if(s===void 0)t=O(this,t,e,0),o=!ie(t)||t!==this._$AH&&t!==P,o&&(this._$AH=t);else{let r=t,l,d;for(t=s[0],l=0;l<s.length-1;l++)d=O(this,r[i+l],e,l),d===P&&(d=this._$AH[l]),o||=!ie(d)||d!==this._$AH[l],d===p?t=p:t!==p&&(t+=(d??"")+s[l+1]),this._$AH[l]=d}o&&!a&&this.j(t)}j(t){t===p?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},fe=class extends U{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===p?void 0:t}},ve=class extends U{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==p)}},we=class extends U{constructor(t,e,i,a,s){super(t,e,i,a,s),this.type=5}_$AI(t,e=this){if((t=O(this,t,e,0)??p)===P)return;let i=this._$AH,a=t===p&&i!==p||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,s=t!==p&&(i===p||a);a&&this.element.removeEventListener(this.name,this,i),s&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},be=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){O(this,t)}},kt={M:Ie,P:_,A:Oe,C:1,L:Lt,R:ge,D:Ct,V:O,I:V,H:U,N:ve,U:we,B:fe,F:be},Hi=Te.litHtmlPolyfillSupport;Hi?.(ae,V),(Te.litHtmlVersions??=[]).push("3.3.3");var Et=(n,t,e)=>{let i=e?.renderBefore??t,a=i._$litPart$;if(a===void 0){let s=e?.renderBefore??null;i._$litPart$=a=new V(t.insertBefore(te(),s),s,void 0,e??{})}return a._$AI(n),a};var Be=globalThis,x=class extends E{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=Et(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return P}};x._$litElement$=!0,x.finalized=!0,Be.litElementHydrateSupport?.({LitElement:x});var ji=Be.litElementPolyfillSupport;ji?.({LitElement:x});(Be.litElementVersions??=[]).push("4.2.2");var _t={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},ye=n=>(...t)=>({_$litDirective$:n,values:t}),N=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};var{I:Ga}=kt;var Pt=(n,t)=>t===void 0?n?._$litType$!==void 0:n?._$litType$===t;var Wi={},Dt=(n,t=Wi)=>n._$AH=t;var zt=ye(class extends N{constructor(){super(...arguments),this.key=p}render(n,t){return this.key=n,t}update(n,[t,e]){return t!==this.key&&(Dt(n),this.key=t),e}});var ne=class extends Error{constructor(e,i,a){super(e);this.deviceCode=i;this.outcomeUnknown=a}},Xi="Restart outcome is unknown. Check the device before trying again.",Yi="Application action outcome is unknown. Check the application before trying again.",Ce="Installation outcome is unknown. Check applications before trying again.",Ki="Policy change outcome is unknown. Check the policy before trying again.",Mt="License change outcome is unknown. Check the application before trying again.",xe=class{constructor(t){this.onStatus=t;this.socket=null;this.connected=!1;this.token="";this.nextId=0;this.pending=new Map}connect(t){this.disconnect(),this.onStatus("connecting"),this.openSocket(t)}openSocket(t){this.token=t;let e=new WebSocket(`ws://${location.host}/api/websocket`);this.socket=e,e.onopen=()=>{this.socket===e&&e.send(JSON.stringify({token:t}))},e.onmessage=i=>{if(this.socket!==e)return;let a=JSON.parse(i.data);if(a.type==="ready"){this.connected=!0,this.onStatus("connected");return}if(a.id===void 0)return;let s=this.pending.get(a.id);if(s){if(a.type==="discovery/device"){a.device&&s.onDiscovered?.(a.device);return}if(a.type==="discovery/warning"){a.message&&s.onWarning?.(a.message);return}clearTimeout(s.timer),this.pending.delete(a.id),a.error?s.reject(new Error(a.error.message)):s.resolve(a.result)}},e.onclose=i=>{if(this.socket===e){if(this.disconnect(),i.code===1008){this.onStatus("denied");return}this.onStatus("reconnecting"),this.reconnectTimer=setTimeout(()=>this.openSocket(t),2e3)}}}disconnect(){clearTimeout(this.reconnectTimer);let t=this.socket;this.socket=null,this.connected=!1,this.token="",t?.close();for(let e of this.pending.values())clearTimeout(e.timer),e.reject(new Error(e.unknownMessage??"Connection lost. Try again once reconnected."));this.pending.clear()}async installApplication(t,e){return this.uploadFile("/api/application-upload",t,e,{"X-Axis-Filename":encodeURIComponent(e.name)},Ce)}async uploadLicense(t,e,i){return this.uploadFile("/api/application-license",t,i,{"X-Axis-Package":encodeURIComponent(e.name),"X-Axis-Version":encodeURIComponent(e.version),"X-Axis-Status":encodeURIComponent(e.status),"X-Axis-License-Status":encodeURIComponent(e.license_status)},Mt)}async updateApplication(t,e,i){return this.requestWrite("/api/application-update",{"Content-Type":"application/json"},JSON.stringify({device:t,filename:i.package.filename,digest:i.package.digest,version:e.version,status:e.status,vendor:e.vendor,warnings:i.warnings,confirmed:!0}),Ce)}async replaceApplication(t,e,i,a){if(!i.replacement)throw new Error("Installation review is unavailable.");return this.requestWrite("/api/application-replace",{"Content-Type":"application/json"},JSON.stringify({device:t,filename:i.package.filename,digest:i.package.digest,version:e.version,status:e.status,vendor:e.vendor,warnings:i.warnings,install_warnings:i.replacement.warnings,remove:a,confirmed:!0}),Ce)}async installCatalogApplication(t,e){return this.requestWrite("/api/application-catalog-install",{"Content-Type":"application/json"},JSON.stringify({device:t,filename:e.package.filename,digest:e.package.digest,warnings:e.warnings,confirmed:!0}),Ce)}async uploadFile(t,e,i,a,s){return this.requestWrite(t,{"X-Axis-Device":encodeURIComponent(e),...a,"X-Axis-Confirmed":"true","Content-Type":"application/octet-stream"},i,s)}async requestWrite(t,e,i,a){if(!this.connected||!this.token)throw new Error("Not connected.");let s;try{s=await fetch(t,{method:"POST",redirect:"error",headers:{"X-Axis-Token":this.token,...e},body:i})}catch{throw new Error(a)}let o;try{o=await s.json()}catch{throw new Error(a)}if(!s.ok){let r=o?.error?.message;throw new ne(typeof r=="string"?r:a,typeof o.error?.device_code=="number"?o.error.device_code:null,o.error?.outcome_unknown===!0)}if(o?.result!==null)throw new Error(a)}callWS(t,e,i,a){let s=this.socket;if(s?.readyState!==WebSocket.OPEN||!this.connected)return Promise.reject(new Error("Not connected."));let o=++this.nextId,r=t==="device/restart"?Xi:t==="device/application-action"?Yi:t==="device/application-policy-set"?Ki:t==="device/application-license-remove"?Mt:void 0;return new Promise((l,d)=>{let u=setTimeout(()=>{this.pending.delete(o),d(new Error(r??"Request timed out."))},65e3);this.pending.set(o,{resolve:g=>l(g),reject:d,timer:u,onDiscovered:i,onWarning:a,unknownMessage:r}),s.send(JSON.stringify({id:o,type:t,...e}))})}};var Ft=n=>n.callWS("devices/list",{}),Rt=(n,t,e)=>n.callWS("devices/discover",{stream:!0},t,e),Tt=(n,t)=>n.callWS("devices/save",t),It=(n,t)=>n.callWS("device/settings",{device:t}),Ot=(n,t,e)=>n.callWS("device/configure",{device:t,...e}),Ut=(n,t)=>n.callWS("device/health",{device:t}),qt=(n,t)=>n.callWS("device/architecture",{device:t}),Bt=(n,t)=>n.callWS("device/apis",{device:t}),Vt=(n,t)=>n.callWS("device/interfaces",{device:t}),Nt=(n,t,e)=>n.callWS("device/read",{device:t,name:e}),Ht=(n,t)=>n.callWS("device/restart",{device:t,confirmed:!0}),Ve=(n,t)=>n.callWS("device/applications",{device:t}),jt=(n,t)=>n.callWS("device/application-support",{device:t}),Wt=(n,t)=>n.callWS("device/acap-updates",{device:t}),Xt=(n,t)=>n.callWS("device/acap-install-candidates",{device:t}),Yt=(n,t,e)=>n.installCatalogApplication(t,e),Kt=(n,t,e,i)=>n.updateApplication(t,e,i),Jt=(n,t)=>n.callWS("device/application-sdks",{device:t}),Gt=(n,t)=>n.callWS("device/application-policy",{device:t}),Zt=(n,t,e,i)=>n.callWS("device/application-policy-set",{device:t,previous:e,value:i,confirmed:!0}),Qt=(n,t,e)=>n.callWS("device/application-license-remove",{device:t,package:e.name,version:e.version,status:e.status,license_status:e.license_status,confirmed:!0}),ei=(n,t,e,i)=>n.uploadLicense(t,e,i),ti=(n,t,e)=>n.installApplication(t,e),ii=(n,t,e,i)=>n.callWS("device/application-action",{device:t,action:i,package:e.name,version:e.version,status:e.status,confirmed:!0});function H(n){return n.alias.trim()||n.discovery?.name.trim()||n.model.trim()||n.serial}var Ji=/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/;function Ne(n){let t=Ji.exec(n);if(!t||t[0]!==n)return null;let e=t[4]?.split(".")??[];return e.some(i=>/^0\d+$/.test(i))?null:{numbers:t.slice(1,4).map(BigInt),prerelease:e}}function ai(n){return Ne(n)!==null}function He(n,t){let e=Ne(n),i=Ne(t);if(!e||!i)return e?-1:i?1:0;for(let a=0;a<3;a++)if(e.numbers[a]!==i.numbers[a])return e.numbers[a]>i.numbers[a]?-1:1;if(!e.prerelease.length||!i.prerelease.length)return e.prerelease.length?1:i.prerelease.length?-1:0;for(let a=0;a<Math.min(e.prerelease.length,i.prerelease.length);a++){let s=e.prerelease[a],o=i.prerelease[a];if(s===o)continue;let r=/^\d+$/.test(s),l=/^\d+$/.test(o);return r!==l?r?1:-1:r?BigInt(s)>BigInt(o)?-1:1:s>o?-1:1}return i.prerelease.length-e.prerelease.length}var Gi=v`
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
    --axis-color-success: light-dark(#006b3c, #85d9a8);
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
    --wa-color-success-fill-quiet: var(--axis-color-surface-muted);
    --wa-color-success-on-quiet: var(--axis-color-success);
    --wa-color-success-border-loud: var(--axis-color-success);
    --wa-color-danger-fill-quiet: var(--axis-color-surface-muted);
    --wa-color-danger-on-quiet: var(--axis-color-danger);
    --wa-color-danger-border-loud: var(--axis-color-danger);
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
`,ni=document.createElement("style");ni.textContent=Gi.cssText;document.head.append(ni);var j=v`
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
`;var z=n=>(t,e)=>{e!==void 0?e.addInitializer(()=>{customElements.define(n,t)}):customElements.define(n,t)};var Zi={attribute:!0,type:String,converter:Q,reflect:!1,hasChanged:ue},Qi=(n=Zi,t,e)=>{let{kind:i,metadata:a}=e,s=globalThis.litPropertyMetadata.get(a);if(s===void 0&&globalThis.litPropertyMetadata.set(a,s=new Map),i==="setter"&&((n=Object.create(n)).wrapped=!0),s.set(e.name,n),i==="accessor"){let{name:o}=e;return{set(r){let l=t.get.call(this);t.set.call(this,r),this.requestUpdate(o,l,n,!0,r)},init(r){return r!==void 0&&this.C(o,void 0,n,r),r}}}if(i==="setter"){let{name:o}=e;return function(r){let l=this[o];t.call(this,r),this.requestUpdate(o,l,n,!0,r)}}throw Error("Unsupported decorator location: "+i)};function h(n){return(t,e)=>typeof e=="object"?Qi(n,t,e):((i,a,s)=>{let o=a.hasOwnProperty(s);return a.constructor.createProperty(s,i),o?Object.getOwnPropertyDescriptor(a,s):void 0})(n,t,e)}function se(n){return h({...n,state:!0,attribute:!1})}var q=(n,t,e)=>(e.configurable=!0,e.enumerable=!0,Reflect.decorate&&typeof t!="object"&&Object.defineProperty(n,t,e),e);function je(n,t){return(e,i,a)=>{let s=o=>o.renderRoot?.querySelector(n)??null;if(t){let{get:o,set:r}=typeof i=="object"?e:a??(()=>{let l=Symbol();return{get(){return this[l]},set(d){this[l]=d}}})();return q(e,i,{get(){let l=o.call(this);return l===void 0&&(l=s(this),(l!==null||this.hasUpdated)&&r.call(this,l)),l}})}return q(e,i,{get(){return s(this)}})}}var oe=ye(class extends N{constructor(n){if(super(n),n.type!==_t.ATTRIBUTE||n.name!=="class"||n.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(n){return" "+Object.keys(n).filter(t=>n[t]).join(" ")+" "}update(n,[t]){if(this.st===void 0){this.st=new Set,n.strings!==void 0&&(this.nt=new Set(n.strings.join(" ").split(/\s/).filter(i=>i!=="")));for(let i in t)t[i]&&!this.nt?.has(i)&&this.st.add(i);return this.render(t)}let e=n.element.classList;for(let i of this.st)i in t||(e.remove(i),this.st.delete(i));for(let i in t){let a=!!t[i];a===this.st.has(i)||this.nt?.has(i)||(a?(e.add(i),this.st.add(i)):(e.remove(i),this.st.delete(i)))}return P}});var S=n=>n??p;var oi=Symbol.for(""),ea=n=>{if(n?.r===oi)return n?._$litStatic$};var We=(n,...t)=>({_$litStatic$:t.reduce((e,i,a)=>e+(s=>{if(s._$litStatic$!==void 0)return s._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${s}. Use 'unsafeStatic' to pass non-literal values, but
            take care to ensure page security.`)})(i)+n[a+1],n[0]),r:oi}),si=new Map,Xe=n=>(t,...e)=>{let i=e.length,a,s,o=[],r=[],l,d=0,u=!1;for(;d<i;){for(l=t[d];d<i&&(s=e[d],(a=ea(s))!==void 0);)l+=a+t[++d],u=!0;d!==i&&r.push(s),o.push(l),d++}if(d===i&&o.push(t[i]),u){let g=o.join("$$lit$$");(t=si.get(g))===void 0&&(o.raw=o,si.set(g,t=o)),e=r}return n(t,...e)},$e=Xe(c),Gn=Xe($t),Zn=Xe(At);var W=class extends Event{constructor(){super("wa-invalid",{bubbles:!0,cancelable:!1,composed:!0})}};var ri={small:"s",medium:"m",large:"l"};var li=new Set;function ci(n,t){t in ri&&!li.has(`${n}:${t}`)&&(li.add(`${n}:${t}`),console.warn(`[${n}] size="${t}" is deprecated. Use size="${ri[t]}" instead. The long-form value will be removed in the next major version.`))}var X=class{constructor(t,...e){this.slotNames=[],this.handleSlotChange=i=>{let a=i.target;(this.slotNames.includes("[default]")&&!a.name||a.name&&this.slotNames.includes(a.name))&&this.host.requestUpdate()},(this.host=t).addController(this),this.slotNames=e}hasDefaultSlot(){return this.host.childNodes?[...this.host.childNodes].some(t=>{if(t.nodeType===Node.TEXT_NODE&&t.textContent.trim()!=="")return!0;if(t.nodeType===Node.ELEMENT_NODE){let e=t;if(e.tagName.toLowerCase()==="wa-visually-hidden")return!1;if(!e.hasAttribute("slot"))return!0}return!1}):!1}hasNamedSlot(t){return this.host.querySelector?.(`:scope > [slot="${t}"]`)!==null}test(t,e){return e&&this.host.didSSR&&!this.host.hasUpdated?!!this.host[e]:t==="[default]"?this.hasDefaultSlot():this.hasNamedSlot(t)}hostConnected(){let t=this.host.shadowRoot;t&&"addEventListener"in t&&t.addEventListener("slotchange",this.handleSlotChange)}hostDisconnected(){let t=this.host.shadowRoot;t&&"removeEventListener"in t&&t.removeEventListener("slotchange",this.handleSlotChange)}};var di=()=>({checkValidity(n){let t=n.input,e={message:"",isValid:!0,invalidKeys:[]};if(!t)return e;let i=!0;if("checkValidity"in t&&(i=t.checkValidity()),i)return e;if(e.isValid=!1,"validationMessage"in t&&(e.message=t.validationMessage),!("validity"in t))return e.invalidKeys.push("customError"),e;for(let a in t.validity){if(a==="valid")continue;let s=a;t.validity[s]&&e.invalidKeys.push(s)}return e}});function M(n,t){let e={waitUntilFirstUpdate:!1,...t};return(i,a)=>{let{update:s}=i,o=Array.isArray(n)?n:[n];i.update=function(r){o.forEach(l=>{let d=l;if(r.has(d)){let u=r.get(d),g=this[d];u!==g&&(!e.waitUntilFirstUpdate||this.hasUpdated)&&this[a](u,g)}}),s.call(this,r)}}}var pi=()=>({observedAttributes:["custom-error"],checkValidity(n){let t={message:"",isValid:!0,invalidKeys:[]};return n.customError&&(t.message=n.customError,t.isValid=!1,t.invalidKeys=["customError"]),t}});var hi=v`:host {
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
`;var Ae=class extends Set{constructor(t,e=null){super(),this._existing=null,this._el=t,this._existing=e}add(t){super.add(t);let e=this._existing;if(e)try{e.add(t)}catch{e.add(`--${t}`)}else this._el.setAttribute(`state-${t}`,"");return this}delete(t){super.delete(t);let e=this._existing;return e?(e.delete(t),e.delete(`--${t}`)):this._el.removeAttribute(`state-${t}`),!0}has(t){return super.has(t)}clear(){for(let t of this)this.delete(t)}};if(typeof CSSStyleSheet<"u"){let n=CSSStyleSheet.prototype.replaceSync;Object.defineProperty(CSSStyleSheet.prototype,"replaceSync",{value:function(t){t=t.replace(/:state\(([^)]+)\)/g,":is(:state($1), :--$1, [state-$1])"),n.call(this,t)}})}var ta=Object.defineProperty,ia=Object.getOwnPropertyDescriptor,mi=n=>{throw TypeError(n)},Ye=(n,t,e,i)=>{for(var a=i>1?void 0:i?ia(t,e):t,s=n.length-1,o;s>=0;s--)(o=n[s])&&(a=(i?o(t,e,a):o(a))||a);return i&&a&&ta(t,e,a),a},gi=(n,t,e)=>t.has(n)||mi("Cannot "+e),aa=(n,t,e)=>(gi(n,t,"read from private field"),e?e.call(n):t.get(n)),na=(n,t,e)=>t.has(n)?mi("Cannot add the same private member more than once"):t instanceof WeakSet?t.add(n):t.set(n,e),sa=(n,t,e,i)=>(gi(n,t,"write to private field"),i?i.call(n,e):t.set(n,e),e),oa=/;\s+$/;function ra(n){return n.replace(/[A-Z]/g,t=>`-${t.toLowerCase()}`)}function ui(n){let{property:t,value:e,element:i}=n;if(e){let a=i.getAttribute("style")||"";a&&(a.match(oa)||(a+=";"),a+=" ");let s=`${t}: ${e}`;return a.includes(s)?void 0:`${a}${s};`}return null}var Se,A=class extends x{constructor(){super(),na(this,Se,!1),this.initialReflectedProperties=new Map,this.didSSR=!!this.shadowRoot,this.customStates={set:(e,i)=>{if(this.internals?.states)try{i?this.internals.states.add(e):this.internals.states.delete(e)}catch(a){if(String(a).includes("must start with '--'"))console.error("Your browser implements an outdated version of CustomStateSet. Consider using a polyfill");else throw a}},has:e=>{if(!this.internals?.states)return!1;try{return this.internals.states.has(e)}catch{return!1}}};try{this.internals=this.attachInternals()}catch{console.error("Element internals are not supported in your browser. Consider using a polyfill")}this.customStates.set("wa-defined",!0);let t=this.constructor;for(let[e,i]of t.elementProperties)i.default==="inherit"&&i.initial!==void 0&&typeof e=="string"&&this.customStates.set(`initial-${e}-${i.initial}`,!0)}static get styles(){let t=Array.isArray(this.css)?this.css:this.css?[this.css]:[];return[hi,...t]}attachInternals(){let t=super.attachInternals();return Object.defineProperty(t,"states",{value:new Ae(this,t.states)}),t}connectedCallback(){super.connectedCallback(),this.didSSR||this.shadowRoot?.prepend(document.createComment(` Web Awesome: https://webawesome.com/docs/components/${this.localName.replace("wa-","")} `)),this.didSSR&&this.updateComplete.then(()=>{this.shadowRoot?.prepend(document.createComment(` Web Awesome: https://webawesome.com/docs/components/${this.localName.replace("wa-","")} `))})}attributeChangedCallback(t,e,i){aa(this,Se)||(this.constructor.elementProperties.forEach((a,s)=>{a.reflect&&this[s]!=null&&this.initialReflectedProperties.set(s,this[s])}),sa(this,Se,!0)),super.attributeChangedCallback(t,e,i)}willUpdate(t){super.willUpdate(t),this.initialReflectedProperties.forEach((e,i)=>{t.has(i)&&this[i]==null&&(this[i]=e)})}firstUpdated(t){super.firstUpdated(t),this.didSSR&&this.shadowRoot?.querySelectorAll("slot").forEach(e=>{e.dispatchEvent(new Event("slotchange",{bubbles:!0,composed:!1,cancelable:!1}))})}update(t){try{super.update(t)}catch(e){if(this.didSSR&&!this.hasUpdated){let i=new Event("lit-hydration-error",{bubbles:!0,composed:!0,cancelable:!1});i.error=e,this.dispatchEvent(i)}throw e}}setStyle(t,e){if(!this.style){let i=ui({property:ra(t),value:e,element:this});i&&this.setAttribute("style",i);return}this.style[t]=e}setStyleProperty(t,e){if(!this.style){let i=ui({property:t,value:e,element:this});i&&this.setAttribute("style",i);return}this.style.setProperty(t,e)}relayNativeEvent(t,e){t.stopImmediatePropagation(),this.dispatchEvent(new t.constructor(t.type,{...t,...e}))}};Se=new WeakMap;Ye([h()],A.prototype,"dir",2);Ye([h()],A.prototype,"lang",2);Ye([h({type:Boolean,reflect:!0,attribute:"did-ssr"})],A.prototype,"didSSR",2);var la=Object.defineProperty,ca=Object.getOwnPropertyDescriptor,Y=(n,t,e,i)=>{for(var a=i>1?void 0:i?ca(t,e):t,s=n.length-1,o;s>=0;s--)(o=n[s])&&(a=(i?o(t,e,a):o(a))||a);return i&&a&&la(t,e,a),a},L=class extends A{constructor(){super(),this.name=null,this.disabled=!1,this.required=!1,this.assumeInteractionOn=["input"],this.validators=[],this.valueHasChanged=!1,this.hasInteracted=!1,this.customError=null,this.emittedEvents=[],this.emitInvalid=t=>{t.target===this&&(this.hasInteracted=!0,this.dispatchEvent(new W))},this.handleInteraction=t=>{let e=this.emittedEvents;e.includes(t.type)||e.push(t.type),e.length===this.assumeInteractionOn?.length&&(this.hasInteracted=!0)},"addEventListener"in this&&this.addEventListener("invalid",this.emitInvalid)}static get validators(){return[pi()]}static get observedAttributes(){let t=new Set(super.observedAttributes||[]);for(let e of this.validators)if(e.observedAttributes)for(let i of e.observedAttributes)t.add(i);return[...t]}connectedCallback(){super.connectedCallback(),this.didSSR&&!this.hasUpdated?this.updateComplete.then(()=>{this.updateValidity()}):this.updateValidity(),this.assumeInteractionOn.forEach(t=>{this.addEventListener?.(t,this.handleInteraction)})}firstUpdated(...t){super.firstUpdated(...t),this.updateValidity()}willUpdate(t){if(!!1&&t.has("customError")&&(this.customError||(this.customError=null),this.setCustomValidity(this.customError||"")),t.has("value")||t.has("disabled")||t.has("defaultValue")){let e=this.value;this.updateFormValue(e)}t.has("disabled")&&(this.customStates.set("disabled",this.disabled),(this.hasAttribute("disabled")||!!1&&!this.matches(":disabled"))&&this.toggleAttribute("disabled",this.disabled)),super.willUpdate(t),this.didSSR&&!this.hasUpdated?this.updateComplete.then(()=>this.updateValidity()):this.updateValidity()}updateFormValue(t){if(Array.isArray(t)){if(this.name){let e=new FormData;for(let i of t)e.append(this.name,i);this.setValue(e,e)}}else this.setValue(t,t)}get labels(){return this.internals.labels}getForm(){return this.internals.form}set form(t){t?this.setAttribute("form",t):this.removeAttribute("form")}get form(){return this.internals.form}get validity(){return this.internals.validity}get willValidate(){return this.internals.willValidate}get validationMessage(){return this.internals.validationMessage}checkValidity(){return this.updateValidity(),this.internals.checkValidity()}reportValidity(){return this.updateValidity(),this.hasInteracted=!0,this.internals.reportValidity()}get validationTarget(){return this.input||void 0}setValidity(...t){let e=t[0],i=t[1],a=t[2];a||(a=this.validationTarget),this.internals.setValidity(e,i,a||void 0),this.requestUpdate("validity"),this.setCustomStates()}setCustomStates(){let t=!!this.required,e=this.internals.validity.valid,i=this.hasInteracted;this.customStates.set("required",t),this.customStates.set("optional",!t),this.customStates.set("invalid",!e),this.customStates.set("valid",e),this.customStates.set("user-invalid",!e&&i),this.customStates.set("user-valid",e&&i)}setCustomValidity(t){if(!t){this.customError=null,this.setValidity({});return}this.customError=t,this.setValidity({customError:!0},t,this.validationTarget)}formResetCallback(){this.resetValidity(),this.hasInteracted=!1,this.valueHasChanged=!1,this.emittedEvents=[],this.updateValidity()}formDisabledCallback(t){this.disabled=t,this.updateValidity()}formStateRestoreCallback(t,e){this.didSSR&&!this.hasUpdated?this.updateComplete.then(()=>{this.value=t,e==="restore"&&this.resetValidity(),this.updateValidity()}):(this.value=t,e==="restore"&&this.resetValidity(),this.updateValidity())}setValue(...t){let[e,i]=t;this.internals.setFormValue(e,i)}get allValidators(){let t=this.constructor.validators||[],e=this.validators||[];return[...t,...e]}resetValidity(){this.setCustomValidity(""),this.setValidity({})}updateValidity(){if(this.disabled||this.hasAttribute("disabled")||!this.willValidate){this.resetValidity();return}let t=this.allValidators;if(!t?.length)return;let e={customError:!!this.customError},i=this.validationTarget||this.input||void 0,a="";for(let s of t){let{isValid:o,message:r,invalidKeys:l}=s.checkValidity(this);o||(a||(a=r),l?.length>=0&&l.forEach(d=>e[d]=!0))}a||(a=this.validationMessage),this.setValidity(e,a,i)}};L.formAssociated=!0;Y([h({reflect:!0})],L.prototype,"name",2);Y([h({type:Boolean})],L.prototype,"disabled",2);Y([h({state:!0,attribute:!1})],L.prototype,"valueHasChanged",2);Y([h({state:!0,attribute:!1})],L.prototype,"hasInteracted",2);Y([h({attribute:"custom-error",reflect:!0})],L.prototype,"customError",2);Y([h({attribute:!1,state:!0,type:Object})],L.prototype,"validity",1);var Le=v`:host([size="xs"]) {
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
`;var fi=v`:where(:root),
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
`;var Ke=new Set,K=new Map,D,Je="ltr",Ge="en",vi=typeof MutationObserver<"u"&&typeof document<"u"&&typeof document.documentElement<"u";if(vi){let n=new MutationObserver(wi);Je=document.documentElement.dir||"ltr",Ge=document.documentElement.lang||navigator.language,n.observe(document.documentElement,{attributes:!0,attributeFilter:["dir","lang"]})}function le(...n){n.map(t=>{let e=t.$code.toLowerCase();K.has(e)?K.set(e,Object.assign(Object.assign({},K.get(e)),t)):K.set(e,t),D||(D=t)}),wi()}function wi(){vi&&(Je=document.documentElement.dir||"ltr",Ge=document.documentElement.lang||navigator.language),[...Ke.keys()].map(n=>{typeof n.requestUpdate=="function"&&n.requestUpdate()})}var ke=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){Ke.add(this.host)}hostDisconnected(){Ke.delete(this.host)}dir(){return`${this.host.dir||Je}`.toLowerCase()}lang(){let t=`${this.host.lang||Ge}`.toLowerCase().replace(/_/g,"-");try{return new Intl.Locale(t),t}catch{return D?D.$code.toLowerCase():"en"}}getTranslationData(t){var e,i;let a;try{a=new Intl.Locale(t.replace(/_/g,"-"))}catch{return{locale:void 0,language:"",region:"",primary:void 0,secondary:void 0}}let s=a.language.toLowerCase(),o=(i=(e=a.region)===null||e===void 0?void 0:e.toLowerCase())!==null&&i!==void 0?i:"",r=K.get(`${s}-${o}`),l=K.get(s);return{locale:a,language:s,region:o,primary:r,secondary:l}}exists(t,e){var i;let{primary:a,secondary:s}=this.getTranslationData((i=e.lang)!==null&&i!==void 0?i:this.lang());return e=Object.assign({includeFallback:!1},e),!!(a&&a[t]||s&&s[t]||e.includeFallback&&D&&D[t])}term(t,...e){let{primary:i,secondary:a}=this.getTranslationData(this.lang()),s;if(i&&i[t])s=i[t];else if(a&&a[t])s=a[t];else if(D&&D[t])s=D[t];else return console.error(`No translation found for: ${String(t)}`),String(t);return typeof s=="function"?s(...e):s}date(t,e){return t=new Date(t),new Intl.DateTimeFormat(this.lang(),e).format(t)}number(t,e){return t=Number(t),isNaN(t)?"":new Intl.NumberFormat(this.lang(),e).format(t)}relativeTime(t,e,i){return new Intl.RelativeTimeFormat(this.lang(),i).format(t,e)}};var bi={$code:"en",$name:"English",$dir:"ltr",allTagsRemoved:"All tags removed",am:"AM",autosizeColumn:"Autosize column",captions:"Captions",carousel:"Carousel",chooseDate:"Choose date",chooseDecade:"Choose decade",chooseMonth:"Choose month",chooseTime:"Choose time",chooseYear:"Choose year",clearEntry:"Clear entry",clearFilter:"Clear filter",clearSort:"Clear sort",close:"Close",closeCalendar:"Close calendar",closeTimeInput:"Close time picker",collapseRow:"Collapse row",columnMenu:"Column options",columnMovedToPosition:(n,t,e)=>`${n} moved to position ${t} of ${e}`,columns:"Columns",compactPageXOfY:(n,t)=>`${n} of ${t}`,completed:"Completed",copied:"Copied",copy:"Copy",createOption:n=>`Create "${n}"`,currentlyPlaying:"currently playing",currentValue:"Current value",date:"Date",datePickerKeyboardHelp:"Use arrow keys to change values; press Alt+Down Arrow to open the calendar.",day:"Day",dayPeriod:"AM/PM",decrement:"Decrement",deselectAllRows:"Deselect all rows",disabled:"Disabled",dropFileHere:"Drop file here or click to browse",dropFilesHere:"Drop files here or click to browse",empty:"Empty",endDate:"End date",enterFullscreen:"Enter fullscreen",error:"Error",exitFullscreen:"Exit fullscreen",expandRow:"Expand row",filterByColumn:n=>`Filter by ${n}`,filterFrom:"From",filterMax:"Max",filterMin:"Min",filterTo:"To",firstPage:"First page",goToSlide:(n,t)=>`Go to slide ${n} of ${t}`,hideColumn:"Hide column",hidePassword:"Hide password",hour:"Hour",incompleteDate:"Enter a valid date.",increment:"Increment",jumpBackwardX:n=>`Jump back ${n} pages`,jumpForwardX:n=>`Jump forward ${n} pages`,lastPage:"Last page",loading:"Loading",locked:"Locked",minute:"Minute",month:"Month",moreOptions:"More Options",mute:"Mute",nextDecade:"Next decade",nextMonth:"Next month",nextPage:"Next page",nextSlide:"Next slide",nextVideo:"Next Video",nextYear:"Next year",noData:"No data",noOptions:"No options",noResults:"No matching results",notCompleted:"Not completed",now:"Now",numCharacters:n=>n===1?"1 character":`${n} characters`,numCharactersRemaining:n=>n===1?"1 character remaining":`${n} characters remaining`,numOptionsAvailable:n=>n===0?"No options available":n===1?"1 option available":`${n} options available`,numOptionsSelected:n=>n===0?"No options selected":n===1?"1 option selected":`${n} options selected`,numRowsCopied:n=>n===1?"1 row copied":`${n} rows copied`,numRowsSelected:n=>n===1?"1 row selected":`${n} rows selected`,optionPosition:(n,t,e)=>`${n}, ${t} of ${e}`,optionsLoadError:"Options could not be loaded",pageXOfY:(n,t)=>`Page ${n} of ${t}`,pagination:"Pagination",pause:"Pause",pauseAnimation:"Pause animation",pictureInPicture:"Picture in picture",pinLeft:"Pin left",pinRight:"Pin right",play:"Play",playAnimation:"Play animation",playbackSpeed:"Playback speed",playlist:"Playlist",pm:"PM",previousDecade:"Previous decade",previousMonth:"Previous month",previousPage:"Previous page",previousSlide:"Previous slide",previousVideo:"Previous video",previousYear:"Previous year",progress:"Progress",rangeTooLong:n=>n===1?"Select a range no longer than 1 day":`Select a range no longer than ${n} days`,rangeTooShort:n=>n===1?"Select a range at least 1 day long":`Select a range at least ${n} days long`,readonly:"Read-only",remove:"Remove",resetColumns:"Reset columns",resize:"Resize",resizeColumn:"Resize column",rowsPerPage:"Rows per page",scrollableRegion:"Scrollable region",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",search:"Search",second:"Second",seek:"Seek",seekProgress:(n,t)=>`${n} of ${t}`,selectAColorFromTheScreen:"Select a color from the screen",selectAllRows:"Select all rows",selected:"Selected",selectedDateLabel:n=>`Selected: ${n}`,selectedRangeLabel:n=>`Selected range: ${n}`,selectGroup:"Select group",selectionCleared:"Selection cleared",selectRow:"Select row",showingNofMRows:(n,t)=>`Showing ${n} of ${t} rows`,showingXtoYofZ:(n,t,e)=>`${n}\u2013${t} of ${e}`,showPassword:"Show password",slideNum:n=>`Slide ${n}`,sortAscending:"Sort ascending",sortColumn:"Sort column",sortDescending:"Sort descending",startDate:"Start date",steps:"Steps",stepXOfY:(n,t)=>`Step ${n} of ${t}`,tagAdded:n=>`${n} added`,tagAlreadyAdded:n=>`${n} is already added`,tagInputKeyboardHelp:"Press Backspace or Delete to remove this tag.",tagRemoved:n=>`${n} removed`,time:"Time",timeInputKeyboardHelp:"Use arrow keys to change values; press Alt+Down Arrow to open the time picker.",today:"Today",toggleColorFormat:"Toggle color format",tooFewTags:n=>n===1?"Add at least 1 tag":`Add at least ${n} tags`,tooManyTags:n=>n===1?"Add no more than 1 tag":`Add no more than ${n} tags`,unmute:"Unmute",unpin:"Unpin",unpinColumn:"Unpin column",videoPlayer:"Video player",volume:"Volume",year:"Year",zoomIn:"Zoom in",zoomOut:"Zoom out"};le(bi);var yi=bi;var J=class extends ke{lang(){return this.host.didSSR&&!this.host.hasUpdated?this.host.lang||"en":super.lang()}};le(yi);var Ee=class extends Event{constructor(){super("wa-error",{bubbles:!0,cancelable:!1,composed:!0})}};var _e=class extends Event{constructor(){super("wa-load",{bubbles:!0,cancelable:!1,composed:!0})}};var Ci=v`:host {
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
`;var da="",Ze="";function xi(){return da.replace(/\/$/,"")}function pa(n){Ze=n}function $i(){if(!Ze){let n=document.querySelector("[data-fa-kit-code]");n&&pa(n.getAttribute("data-fa-kit-code")||"")}return Ze}var Ai="7.3.0";function ha(n,t,e){let i="solid";return t==="chisel"&&(i="chisel-regular"),t==="etch"&&(i="etch-solid"),t==="graphite"&&(i="graphite-thin"),t==="jelly"&&(i="jelly-regular",e==="duo-regular"&&(i="jelly-duo-regular"),e==="fill-regular"&&(i="jelly-fill-regular")),t==="jelly-duo"&&(i="jelly-duo-regular"),t==="jelly-fill"&&(i="jelly-fill-regular"),t==="notdog"&&(e==="solid"&&(i="notdog-solid"),e==="duo-solid"&&(i="notdog-duo-solid")),t==="notdog-duo"&&(i="notdog-duo-solid"),t==="slab"&&((e==="solid"||e==="regular")&&(i="slab-regular"),e==="press-regular"&&(i="slab-press-regular")),t==="slab-press"&&(i="slab-press-regular"),t==="slab-duo"&&(i="slab-duo-regular"),t==="slab-press-duo"&&(i="slab-press-duo-regular"),t==="thumbprint"&&(i="thumbprint-light"),t==="utility"&&(i="utility-semibold"),t==="utility-duo"&&(i="utility-duo-semibold"),t==="utility-fill"&&(i="utility-fill-semibold"),t==="whiteboard"&&(i="whiteboard-semibold"),t==="mosaic"&&(i="mosaic-solid"),t==="pixel"&&(i="pixel-regular"),t==="vellum"&&(i="vellum-solid"),t==="classic"&&(e==="thin"&&(i="thin"),e==="light"&&(i="light"),e==="regular"&&(i="regular"),e==="solid"&&(i="solid")),t==="duotone"&&(e==="thin"&&(i="duotone-thin"),e==="light"&&(i="duotone-light"),e==="regular"&&(i="duotone-regular"),e==="solid"&&(i="duotone")),t==="sharp"&&(e==="thin"&&(i="sharp-thin"),e==="light"&&(i="sharp-light"),e==="regular"&&(i="sharp-regular"),e==="solid"&&(i="sharp-solid")),t==="sharp-duotone"&&(e==="thin"&&(i="sharp-duotone-thin"),e==="light"&&(i="sharp-duotone-light"),e==="regular"&&(i="sharp-duotone-regular"),e==="solid"&&(i="sharp-duotone-solid")),t==="brands"&&(i="brands"),i}function ua(n,t,e){let i=ha(n,t,e),a=xi();if(a)return`${a}/${i}/${n}.svg`;let s=$i();return s.length>0?`https://ka-p.fontawesome.com/releases/v${Ai}/svgs/${i}/${n}.svg?token=${encodeURIComponent(s)}`:`https://ka-f.fontawesome.com/releases/v${Ai}/svgs/${i}/${n}.svg`}var ma={name:"default",resolver:(n,t="classic",e="solid")=>ua(n,t,e),mutator:(n,t)=>{if(n.hasAttribute("fill")||n.setAttribute("fill","currentColor"),t?.family&&!n.hasAttribute("data-duotone-initialized")){let{family:e,variant:i}=t;if(e==="duotone"||e==="sharp-duotone"||e==="notdog-duo"||e==="notdog"&&i==="duo-solid"||e==="jelly-duo"||e==="jelly"&&i==="duo-regular"||e==="utility-duo"||e==="slab-duo"||e==="slab-press-duo"||e==="thumbprint"){let a=[...n.querySelectorAll("path")],s=a.find(r=>!r.hasAttribute("opacity")),o=a.find(r=>r.hasAttribute("opacity"));if(!s||!o)return;if(s.setAttribute("data-duotone-primary",""),o.setAttribute("data-duotone-secondary",""),t.swapOpacity&&s&&o){let r=o.getAttribute("opacity")||"0.4";s.style.setProperty("--path-opacity",r),o.style.setProperty("--path-opacity","1")}n.setAttribute("data-duotone-initialized","")}}}},Si=ma;function ga(n){return`data:image/svg+xml,${encodeURIComponent(n)}`}var Qe={solid:{"arrow-down":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M169.4 502.6c12.5 12.5 32.8 12.5 45.3 0l160-160c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 402.7 224 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 370.7-105.4-105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160z"/></svg>',"arrow-up":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M214.6 9.4c-12.5-12.5-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 480c0 17.7 14.3 32 32 32s32-14.3 32-32l0-370.7 105.4 105.4c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-160-160z"/></svg>',backward:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M236.3 107.1C247.9 96 265 92.9 279.7 99.2C294.4 105.5 304 120 304 136L304 272.3L476.3 107.2C487.9 96 505 92.9 519.7 99.2C534.4 105.5 544 120 544 136L544 504C544 520 534.4 534.5 519.7 540.8C505 547.1 487.9 544 476.3 532.9L304 367.7L304 504C304 520 294.4 534.5 279.7 540.8C265 547.1 247.9 544 236.3 532.9L44.3 348.9C36.5 341.3 32 330.9 32 320C32 309.1 36.5 298.7 44.3 291.1L236.3 107.1z"/></svg>',"backward-step":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M491 100.8C478.1 93.8 462.3 94.5 450 102.6L192 272.1L192 128C192 110.3 177.7 96 160 96C142.3 96 128 110.3 128 128L128 512C128 529.7 142.3 544 160 544C177.7 544 192 529.7 192 512L192 367.9L450 537.5C462.3 545.6 478 546.3 491 539.3C504 532.3 512 518.8 512 504.1L512 136.1C512 121.4 503.9 107.9 491 100.9z"/></svg>',bars:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.3.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2026 Fonticons, Inc. --><path d="M0 96C0 78.3 14.3 64 32 64l384 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 128C14.3 128 0 113.7 0 96zM0 256c0-17.7 14.3-32 32-32l384 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 288c-17.7 0-32-14.3-32-32zM448 416c0 17.7-14.3 32-32 32L32 448c-17.7 0-32-14.3-32-32s14.3-32 32-32l384 0c17.7 0 32 14.3 32 32z"/></svg>',"angles-left":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M77.3 256 214.7 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256zm192 0L406.7 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L269.3 256z"/></svg>',"angles-right":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M434.7 256 297.3 118.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l160 160c12.5 12.5 12.5 32.8 0 45.3l-160 160c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L434.7 256zm-192 0L105.3 118.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l160 160c12.5 12.5 12.5 32.8 0 45.3l-160 160c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L242.7 256z"/></svg>',check:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M434.8 70.1c14.3 10.4 17.5 30.4 7.1 44.7l-256 352c-5.5 7.6-14 12.3-23.4 13.1s-18.5-2.7-25.1-9.3l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l101.5 101.5 234-321.7c10.4-14.3 30.4-17.5 44.7-7.1z"/></svg>',"chevron-down":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M201.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 338.7 54.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"/></svg>',"chevron-left":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l192 192c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256 246.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-192 192z"/></svg>',"chevron-right":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M311.1 233.4c12.5 12.5 12.5 32.8 0 45.3l-192 192c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L243.2 256 73.9 86.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l192 192z"/></svg>',circle:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0z"/></svg>',"closed-captioning":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M64 192C64 156.7 92.7 128 128 128L512 128C547.3 128 576 156.7 576 192L576 448C576 483.3 547.3 512 512 512L128 512C92.7 512 64 483.3 64 448L64 192zM216 272L248 272C252.4 272 256 275.6 256 280C256 293.3 266.7 304 280 304C293.3 304 304 293.3 304 280C304 249.1 278.9 224 248 224L216 224C185.1 224 160 249.1 160 280L160 360C160 390.9 185.1 416 216 416L248 416C278.9 416 304 390.9 304 360C304 346.7 293.3 336 280 336C266.7 336 256 346.7 256 360C256 364.4 252.4 368 248 368L216 368C211.6 368 208 364.4 208 360L208 280C208 275.6 211.6 272 216 272zM384 280C384 275.6 387.6 272 392 272L424 272C428.4 272 432 275.6 432 280C432 293.3 442.7 304 456 304C469.3 304 480 293.3 480 280C480 249.1 454.9 224 424 224L392 224C361.1 224 336 249.1 336 280L336 360C336 390.9 361.1 416 392 416L424 416C454.9 416 480 390.9 480 360C480 346.7 469.3 336 456 336C442.7 336 432 346.7 432 360C432 364.4 428.4 368 424 368L392 368C387.6 368 384 364.4 384 360L384 280z"/></svg>',"closed-captioning-slash":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M39 39.1C48.4 29.7 63.6 29.7 72.9 39.1L161.8 128L512 128C547.3 128 576 156.7 576 192L576 448C576 473.5 561.1 495.4 539.6 505.8L601 567.1C610.4 576.5 610.4 591.7 601 601C591.6 610.3 576.4 610.4 567.1 601L39 73.1C29.7 63.7 29.7 48.5 39 39.1zM384 350.1L384 279.9C384 275.5 387.6 271.9 392 271.9L424 271.9C428.4 271.9 432 275.5 432 279.9C432 293.2 442.7 303.9 456 303.9C469.3 303.9 480 293.2 480 279.9C480 249 454.9 223.9 424 223.9L392 223.9C361.1 223.9 336 249 336 279.9L336 302.1L384 350.1zM445.5 411.6C465.7 403.2 480 383.2 480 359.9C480 346.6 469.3 335.9 456 335.9C442.7 335.9 432 346.6 432 359.9C432 364.3 428.4 367.9 424 367.9L401.8 367.9L445.5 411.6zM162.3 264.1C160.8 269.1 160 274.5 160 280L160 360C160 390.9 185.1 416 216 416L248 416C266.1 416 282.1 407.5 292.4 394.2L410.2 512L128 512C92.7 512 64 483.3 64 448L64 192C64 184.2 65.4 176.7 68 169.8L162.3 264.1zM256.1 357.9C256 358.6 256 359.3 256 360C256 364.4 252.4 368 248 368L216 368C211.6 368 208 364.4 208 360L208 309.8L256.1 357.9z"/></svg>',compress:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M160 64c0-17.7-14.3-32-32-32S96 46.3 96 64l0 64-64 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c17.7 0 32-14.3 32-32l0-96zM32 320c-17.7 0-32 14.3-32 32s14.3 32 32 32l64 0 0 64c0 17.7 14.3 32 32 32s32-14.3 32-32l0-96c0-17.7-14.3-32-32-32l-96 0zM352 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32l96 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-64 0 0-64zM320 320c-17.7 0-32 14.3-32 32l0 96c0 17.7 14.3 32 32 32s32-14.3 32-32l0-64 64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-96 0z"/></svg>',ellipsis:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.3.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M96 320C96 289.1 121.1 264 152 264C182.9 264 208 289.1 208 320C208 350.9 182.9 376 152 376C121.1 376 96 350.9 96 320zM264 320C264 289.1 289.1 264 320 264C350.9 264 376 289.1 376 320C376 350.9 350.9 376 320 376C289.1 376 264 350.9 264 320zM488 264C518.9 264 544 289.1 544 320C544 350.9 518.9 376 488 376C457.1 376 432 350.9 432 320C432 289.1 457.1 264 488 264z"/></svg>',"ellipsis-vertical":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M320 208C289.1 208 264 182.9 264 152C264 121.1 289.1 96 320 96C350.9 96 376 121.1 376 152C376 182.9 350.9 208 320 208zM320 432C350.9 432 376 457.1 376 488C376 518.9 350.9 544 320 544C289.1 544 264 518.9 264 488C264 457.1 289.1 432 320 432zM376 320C376 350.9 350.9 376 320 376C289.1 376 264 350.9 264 320C264 289.1 289.1 264 320 264C350.9 264 376 289.1 376 320z"/></svg>',expand:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 96C110.3 96 96 110.3 96 128L96 224C96 241.7 110.3 256 128 256C145.7 256 160 241.7 160 224L160 160L224 160C241.7 160 256 145.7 256 128C256 110.3 241.7 96 224 96L128 96zM160 416C160 398.3 145.7 384 128 384C110.3 384 96 398.3 96 416L96 512C96 529.7 110.3 544 128 544L224 544C241.7 544 256 529.7 256 512C256 494.3 241.7 480 224 480L160 480L160 416zM416 96C398.3 96 384 110.3 384 128C384 145.7 398.3 160 416 160L480 160L480 224C480 241.7 494.3 256 512 256C529.7 256 544 241.7 544 224L544 128C544 110.3 529.7 96 512 96L416 96zM544 416C544 398.3 529.7 384 512 384C494.3 384 480 398.3 480 416L480 480L416 480C398.3 480 384 494.3 384 512C384 529.7 398.3 544 416 544L512 544C529.7 544 544 529.7 544 512L544 416z"/></svg>',eyedropper:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M341.6 29.2l-101.6 101.6-9.4-9.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-9.4-9.4 101.6-101.6c39-39 39-102.2 0-141.1s-102.2-39-141.1 0zM55.4 323.3c-15 15-23.4 35.4-23.4 56.6l0 42.4-26.6 39.9c-8.5 12.7-6.8 29.6 4 40.4s27.7 12.5 40.4 4l39.9-26.6 42.4 0c21.2 0 41.6-8.4 56.6-23.4l109.4-109.4-45.3-45.3-109.4 109.4c-3 3-7.1 4.7-11.3 4.7l-36.1 0 0-36.1c0-4.2 1.7-8.3 4.7-11.3l109.4-109.4-45.3-45.3-109.4 109.4z"/></svg>',filter:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M32 64C19.1 64 7.4 71.8 2.4 83.8S.2 109.5 9.4 118.6L192 301.3 192 416c0 8.5 3.4 16.6 9.4 22.6l64 64c9.2 9.2 22.9 11.9 34.9 6.9S320 492.9 320 480l0-178.7 182.6-182.6c9.2-9.2 11.9-22.9 6.9-34.9S492.9 64 480 64L32 64z"/></svg>',forward:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M403.7 107.1C392.1 96 375 92.9 360.3 99.2C345.6 105.5 336 120 336 136L336 272.3L163.7 107.2C152.1 96 135 92.9 120.3 99.2C105.6 105.5 96 120 96 136L96 504C96 520 105.6 534.5 120.3 540.8C135 547.1 152.1 544 163.7 532.9L336 367.7L336 504C336 520 345.6 534.5 360.3 540.8C375 547.1 392.1 544 403.7 532.9L595.7 348.9C603.6 341.4 608 330.9 608 320C608 309.1 603.5 298.7 595.7 291.1L403.7 107.1z"/></svg>',file:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M192 64C156.7 64 128 92.7 128 128L128 512C128 547.3 156.7 576 192 576L448 576C483.3 576 512 547.3 512 512L512 234.5C512 217.5 505.3 201.2 493.3 189.2L386.7 82.7C374.7 70.7 358.5 64 341.5 64L192 64zM453.5 240L360 240C346.7 240 336 229.3 336 216L336 122.5L453.5 240z"/></svg>',"file-audio":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM389.8 307.7C380.7 301.4 368.3 303.6 362 312.7C355.7 321.8 357.9 334.2 367 340.5C390.9 357.2 406.4 384.8 406.4 416C406.4 447.2 390.8 474.9 367 491.5C357.9 497.8 355.7 510.3 362 519.3C368.3 528.3 380.8 530.6 389.8 524.3C423.9 500.5 446.4 460.8 446.4 416C446.4 371.2 424 331.5 389.8 307.7zM208 376C199.2 376 192 383.2 192 392L192 440C192 448.8 199.2 456 208 456L232 456L259.2 490C262.2 493.8 266.8 496 271.7 496L272 496C280.8 496 288 488.8 288 480L288 352C288 343.2 280.8 336 272 336L271.7 336C266.8 336 262.2 338.2 259.2 342L232 376L208 376zM336 448.2C336 458.9 346.5 466.4 354.9 459.8C367.8 449.5 376 433.7 376 416C376 398.3 367.8 382.5 354.9 372.2C346.5 365.5 336 373.1 336 383.8L336 448.3z"/></svg>',"file-code":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM282.2 359.6C290.8 349.5 289.7 334.4 279.6 325.8C269.5 317.2 254.4 318.3 245.8 328.4L197.8 384.4C190.1 393.4 190.1 406.6 197.8 415.6L245.8 471.6C254.4 481.7 269.6 482.8 279.6 474.2C289.6 465.6 290.8 450.4 282.2 440.4L247.6 400L282.2 359.6zM394.2 328.4C385.6 318.3 370.4 317.2 360.4 325.8C350.4 334.4 349.2 349.6 357.8 359.6L392.4 400L357.8 440.4C349.2 450.5 350.3 465.6 360.4 474.2C370.5 482.8 385.6 481.7 394.2 471.6L442.2 415.6C449.9 406.6 449.9 393.4 442.2 384.4L394.2 328.4z"/></svg>',"file-excel":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM292 330.7C284.6 319.7 269.7 316.7 258.7 324C247.7 331.3 244.7 346.3 252 357.3L291.2 416L252 474.7C244.6 485.7 247.6 500.6 258.7 508C269.8 515.4 284.6 512.4 292 501.3L320 459.3L348 501.3C355.4 512.3 370.3 515.3 381.3 508C392.3 500.7 395.3 485.7 388 474.7L348.8 416L388 357.3C395.4 346.3 392.4 331.4 381.3 324C370.2 316.6 355.4 319.6 348 330.7L320 372.7L292 330.7z"/></svg>',"file-image":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM256 320C256 302.3 241.7 288 224 288C206.3 288 192 302.3 192 320C192 337.7 206.3 352 224 352C241.7 352 256 337.7 256 320zM220.6 512L419.4 512C435.2 512 448 499.2 448 483.4C448 476.1 445.2 469 440.1 463.7L343.3 361.9C337.3 355.6 328.9 352 320.1 352L319.8 352C311 352 302.7 355.6 296.6 361.9L199.9 463.7C194.8 469 192 476.1 192 483.4C192 499.2 204.8 512 220.6 512z"/></svg>',"file-pdf":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 64C92.7 64 64 92.7 64 128L64 512C64 547.3 92.7 576 128 576L208 576L208 464C208 428.7 236.7 400 272 400L448 400L448 234.5C448 217.5 441.3 201.2 429.3 189.2L322.7 82.7C310.7 70.7 294.5 64 277.5 64L128 64zM389.5 240L296 240C282.7 240 272 229.3 272 216L272 122.5L389.5 240zM272 444C261 444 252 453 252 464L252 592C252 603 261 612 272 612C283 612 292 603 292 592L292 564L304 564C337.1 564 364 537.1 364 504C364 470.9 337.1 444 304 444L272 444zM304 524L292 524L292 484L304 484C315 484 324 493 324 504C324 515 315 524 304 524zM400 444C389 444 380 453 380 464L380 592C380 603 389 612 400 612L432 612C460.7 612 484 588.7 484 560L484 496C484 467.3 460.7 444 432 444L400 444zM420 572L420 484L432 484C438.6 484 444 489.4 444 496L444 560C444 566.6 438.6 572 432 572L420 572zM508 464L508 592C508 603 517 612 528 612C539 612 548 603 548 592L548 548L576 548C587 548 596 539 596 528C596 517 587 508 576 508L548 508L548 484L576 484C587 484 596 475 596 464C596 453 587 444 576 444L528 444C517 444 508 453 508 464z"/></svg>',"file-powerpoint":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM280 320C266.7 320 256 330.7 256 344L256 488C256 501.3 266.7 512 280 512C293.3 512 304 501.3 304 488L304 464L328 464C367.8 464 400 431.8 400 392C400 352.2 367.8 320 328 320L280 320zM328 416L304 416L304 368L328 368C341.3 368 352 378.7 352 392C352 405.3 341.3 416 328 416z"/></svg>',"file-video":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM208 368L208 464C208 481.7 222.3 496 240 496L336 496C353.7 496 368 481.7 368 464L368 440L403 475C406.2 478.2 410.5 480 415 480C424.4 480 432 472.4 432 463L432 368.9C432 359.5 424.4 351.9 415 351.9C410.5 351.9 406.2 353.7 403 356.9L368 391.9L368 367.9C368 350.2 353.7 335.9 336 335.9L240 335.9C222.3 335.9 208 350.2 208 367.9z"/></svg>',"file-word":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM263.4 338.8C260.5 325.9 247.7 317.7 234.8 320.6C221.9 323.5 213.7 336.3 216.6 349.2L248.6 493.2C250.9 503.7 260 511.4 270.8 512C281.6 512.6 291.4 505.9 294.8 495.6L320 419.9L345.2 495.6C348.6 505.8 358.4 512.5 369.2 512C380 511.5 389.1 503.8 391.4 493.2L423.4 349.2C426.3 336.3 418.1 323.4 405.2 320.6C392.3 317.8 379.4 325.9 376.6 338.8L363.4 398.2L342.8 336.4C339.5 326.6 330.4 320 320 320C309.6 320 300.5 326.6 297.2 336.4L276.6 398.2L263.4 338.8z"/></svg>',"file-zipper":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M128 128C128 92.7 156.7 64 192 64L341.5 64C358.5 64 374.8 70.7 386.8 82.7L493.3 189.3C505.3 201.3 512 217.6 512 234.6L512 512C512 547.3 483.3 576 448 576L192 576C156.7 576 128 547.3 128 512L128 128zM336 122.5L336 216C336 229.3 346.7 240 360 240L453.5 240L336 122.5zM192 136C192 149.3 202.7 160 216 160L264 160C277.3 160 288 149.3 288 136C288 122.7 277.3 112 264 112L216 112C202.7 112 192 122.7 192 136zM192 232C192 245.3 202.7 256 216 256L264 256C277.3 256 288 245.3 288 232C288 218.7 277.3 208 264 208L216 208C202.7 208 192 218.7 192 232zM256 304L224 304C206.3 304 192 318.3 192 336L192 384C192 410.5 213.5 432 240 432C266.5 432 288 410.5 288 384L288 336C288 318.3 273.7 304 256 304zM240 368C248.8 368 256 375.2 256 384C256 392.8 248.8 400 240 400C231.2 400 224 392.8 224 384C224 375.2 231.2 368 240 368z"/></svg>',"forward-step":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M21 36.8c12.9-7 28.7-6.3 41 1.8L320 208.1 320 64c0-17.7 14.3-32 32-32s32 14.3 32 32l0 384c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-144.1-258 169.6c-12.3 8.1-28 8.8-41 1.8S0 454.7 0 440L0 72C0 57.3 8.1 43.8 21 36.8z"/></svg>',gauge:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zm320 96c0-26.9-16.5-49.9-40-59.3L280 120c0-13.3-10.7-24-24-24s-24 10.7-24 24l0 172.7c-23.5 9.5-40 32.5-40 59.3 0 35.3 28.7 64 64 64s64-28.7 64-64zM144 176a32 32 0 1 0 0-64 32 32 0 1 0 0 64zm-16 80a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm288 32a32 32 0 1 0 0-64 32 32 0 1 0 0 64zM400 144a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"/></svg>',gear:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M259.1 73.5C262.1 58.7 275.2 48 290.4 48L350.2 48C365.4 48 378.5 58.7 381.5 73.5L396 143.5C410.1 149.5 423.3 157.2 435.3 166.3L503.1 143.8C517.5 139 533.3 145 540.9 158.2L570.8 210C578.4 223.2 575.7 239.8 564.3 249.9L511 297.3C511.9 304.7 512.3 312.3 512.3 320C512.3 327.7 511.8 335.3 511 342.7L564.4 390.2C575.8 400.3 578.4 417 570.9 430.1L541 481.9C533.4 495 517.6 501.1 503.2 496.3L435.4 473.8C423.3 482.9 410.1 490.5 396.1 496.6L381.7 566.5C378.6 581.4 365.5 592 350.4 592L290.6 592C275.4 592 262.3 581.3 259.3 566.5L244.9 496.6C230.8 490.6 217.7 482.9 205.6 473.8L137.5 496.3C123.1 501.1 107.3 495.1 99.7 481.9L69.8 430.1C62.2 416.9 64.9 400.3 76.3 390.2L129.7 342.7C128.8 335.3 128.4 327.7 128.4 320C128.4 312.3 128.9 304.7 129.7 297.3L76.3 249.8C64.9 239.7 62.3 223 69.8 209.9L99.7 158.1C107.3 144.9 123.1 138.9 137.5 143.7L205.3 166.2C217.4 157.1 230.6 149.5 244.6 143.4L259.1 73.5zM320.3 400C364.5 399.8 400.2 363.9 400 319.7C399.8 275.5 363.9 239.8 319.7 240C275.5 240.2 239.8 276.1 240 320.3C240.2 364.5 276.1 400.2 320.3 400z"/></svg>',"grip-vertical":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M128 40c0-22.1-17.9-40-40-40L40 0C17.9 0 0 17.9 0 40L0 88c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48zm0 192c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48zM0 424l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM320 40c0-22.1-17.9-40-40-40L232 0c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48zM192 232l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40zM320 424c0-22.1-17.9-40-40-40l-48 0c-22.1 0-40 17.9-40 40l0 48c0 22.1 17.9 40 40 40l48 0c22.1 0 40-17.9 40-40l0-48z"/></svg>',indeterminate:'<svg part="indeterminate-icon" class="icon" viewBox="0 0 16 16"><g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round"><g stroke="currentColor" stroke-width="2"><g transform="translate(2.285714 6.857143)"><path d="M10.2857143,1.14285714 L1.14285714,1.14285714"/></g></g></g></svg>',"magnifying-glass":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376C296.3 401.1 253.9 416 208 416 93.1 416 0 322.9 0 208S93.1 0 208 0 416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/></svg>',minus:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M0 256c0-17.7 14.3-32 32-32l384 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 288c-17.7 0-32-14.3-32-32z"/></svg>',pause:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M48 32C21.5 32 0 53.5 0 80L0 432c0 26.5 21.5 48 48 48l64 0c26.5 0 48-21.5 48-48l0-352c0-26.5-21.5-48-48-48L48 32zm224 0c-26.5 0-48 21.5-48 48l0 352c0 26.5 21.5 48 48 48l64 0c26.5 0 48-21.5 48-48l0-352c0-26.5-21.5-48-48-48l-64 0z"/></svg>',"picture-in-picture":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M448 32c35.3 0 64 28.7 64 64l0 112-64 0 0-112-384 0 0 320 144 0 0 64-144 0-6.5-.3c-30.1-3.1-54.1-27-57.1-57.1L0 416 0 96C0 62.9 25.2 35.6 57.5 32.3L64 32 448 32zm16 224c26.5 0 48 21.5 48 48l0 128c0 26.5-21.5 48-48 48l-160 0c-26.5 0-48-21.5-48-48l0-128c0-26.5 21.5-48 48-48l160 0z"/></svg>',play:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M91.2 36.9c-12.4-6.8-27.4-6.5-39.6 .7S32 57.9 32 72l0 368c0 14.1 7.5 27.2 19.6 34.4s27.2 7.5 39.6 .7l336-184c12.8-7 20.8-20.5 20.8-35.1s-8-28.1-20.8-35.1l-336-184z"/></svg>',"play-circle":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zM188.3 147.1c-7.6 4.2-12.3 12.3-12.3 20.9l0 176c0 8.7 4.7 16.7 12.3 20.9s16.8 4.1 24.3-.5l144-88c7.1-4.4 11.5-12.1 11.5-20.5s-4.4-16.1-11.5-20.5l-144-88c-7.4-4.5-16.7-4.7-24.3-.5z"/></svg>',plus:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M352 128C352 110.3 337.7 96 320 96C302.3 96 288 110.3 288 128L288 288L128 288C110.3 288 96 302.3 96 320C96 337.7 110.3 352 128 352L288 352L288 512C288 529.7 302.3 544 320 544C337.7 544 352 529.7 352 512L352 352L512 352C529.7 352 544 337.7 544 320C544 302.3 529.7 288 512 288L352 288L352 128z"/></svg>',star:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M309.5-18.9c-4.1-8-12.4-13.1-21.4-13.1s-17.3 5.1-21.4 13.1L193.1 125.3 33.2 150.7c-8.9 1.4-16.3 7.7-19.1 16.3s-.5 18 5.8 24.4l114.4 114.5-25.2 159.9c-1.4 8.9 2.3 17.9 9.6 23.2s16.9 6.1 25 2L288.1 417.6 432.4 491c8 4.1 17.7 3.3 25-2s11-14.2 9.6-23.2L441.7 305.9 556.1 191.4c6.4-6.4 8.6-15.8 5.8-24.4s-10.1-14.9-19.1-16.3L383 125.3 309.5-18.9z"/></svg>',"table-columns":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M0 96C0 60.7 28.7 32 64 32l320 0c35.3 0 64 28.7 64 64l0 320c0 35.3-28.7 64-64 64L64 480c-35.3 0-64-28.7-64-64L0 96zm64 64l0 256 128 0 0-256-128 0zm320 0l-128 0 0 256 128 0 0-256z"/></svg>',thumbtack:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M32 32C32 14.3 46.3 0 64 0L320 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-29.5 0 10.3 134.1c37.1 21.2 65.8 56.4 78.2 99.7l3.8 13.4c2.8 9.7 .8 20-5.2 28.1S362 352 352 352L32 352c-10 0-19.5-4.7-25.5-12.7s-8-18.4-5.2-28.1L5 297.8c12.4-43.3 41-78.5 78.2-99.7L93.5 64 64 64C46.3 64 32 49.7 32 32zM160 400l64 0 0 112c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-112z"/></svg>',"up-down":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M406.6 502.6l96-96c9.2-9.2 11.9-22.9 6.9-34.9S492.9 352 480 352l-64 0 0-320c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 320-64 0c-12.9 0-24.6 7.8-29.6 19.8s-2.2 25.7 6.9 34.9l96 96c12.5 12.5 32.8 12.5 45.3 0zM150.6 9.4c-12.5-12.5-32.8-12.5-45.3 0l-96 96c-9.2 9.2-11.9 22.9-6.9 34.9S19.1 160 32 160l64 0 0 320c0 17.7 14.3 32 32 32s32-14.3 32-32l0-320 64 0c12.9 0 24.6-7.8 29.6-19.8s2.2-25.7-6.9-34.9l-96-96z"/></svg>',upload:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free 7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M352 173.3L352 384C352 401.7 337.7 416 320 416C302.3 416 288 401.7 288 384L288 173.3L246.6 214.7C234.1 227.2 213.8 227.2 201.3 214.7C188.8 202.2 188.8 181.9 201.3 169.4L297.3 73.4C309.8 60.9 330.1 60.9 342.6 73.4L438.6 169.4C451.1 181.9 451.1 202.2 438.6 214.7C426.1 227.2 405.8 227.2 393.3 214.7L352 173.3zM320 464C364.2 464 400 428.2 400 384L480 384C515.3 384 544 412.7 544 448L544 480C544 515.3 515.3 544 480 544L160 544C124.7 544 96 515.3 96 480L96 448C96 412.7 124.7 384 160 384L240 384C240 428.2 275.8 464 320 464zM464 488C477.3 488 488 477.3 488 464C488 450.7 477.3 440 464 440C450.7 440 440 450.7 440 464C440 477.3 450.7 488 464 488z"/></svg>',user:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M224 248a120 120 0 1 0 0-240 120 120 0 1 0 0 240zm-29.7 56C95.8 304 16 383.8 16 482.3 16 498.7 29.3 512 45.7 512l356.6 0c16.4 0 29.7-13.3 29.7-29.7 0-98.5-79.8-178.3-178.3-178.3l-59.4 0z"/></svg>',volume:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M48 352l48 0 134.1 119.2c6.4 5.7 14.6 8.8 23.1 8.8 19.2 0 34.8-15.6 34.8-34.8l0-378.4c0-19.2-15.6-34.8-34.8-34.8-8.5 0-16.7 3.1-23.1 8.8L96 160 48 160c-26.5 0-48 21.5-48 48l0 96c0 26.5 21.5 48 48 48zM441.1 107c-10.3-8.4-25.4-6.8-33.8 3.5s-6.8 25.4 3.5 33.8C443.3 170.7 464 210.9 464 256s-20.7 85.3-53.2 111.8c-10.3 8.4-11.8 23.5-3.5 33.8s23.5 11.8 33.8 3.5c43.2-35.2 70.9-88.9 70.9-149s-27.7-113.8-70.9-149zm-60.5 74.5c-10.3-8.4-25.4-6.8-33.8 3.5s-6.8 25.4 3.5 33.8C361.1 227.6 368 241 368 256s-6.9 28.4-17.7 37.3c-10.3 8.4-11.8 23.5-3.5 33.8s23.5 11.8 33.8 3.5C402.1 312.9 416 286.1 416 256s-13.9-56.9-35.5-74.5z"/></svg>',"volume-low":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M48 352l48 0 134.1 119.2c6.4 5.7 14.6 8.8 23.1 8.8 19.2 0 34.8-15.6 34.8-34.8l0-378.4c0-19.2-15.6-34.8-34.8-34.8-8.5 0-16.7 3.1-23.1 8.8L96 160 48 160c-26.5 0-48 21.5-48 48l0 96c0 26.5 21.5 48 48 48zM380.6 181.5c-10.3-8.4-25.4-6.8-33.8 3.5s-6.8 25.4 3.5 33.8C361.1 227.6 368 241 368 256s-6.9 28.4-17.7 37.3c-10.3 8.4-11.8 23.5-3.5 33.8s23.5 11.8 33.8 3.5C402.1 312.9 416 286.1 416 256s-13.9-56.9-35.5-74.5z"/></svg>',"volume-xmark":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M48 352l48 0 134.1 119.2c6.4 5.7 14.6 8.8 23.1 8.8 19.2 0 34.8-15.6 34.8-34.8l0-378.4c0-19.2-15.6-34.8-34.8-34.8-8.5 0-16.7 3.1-23.1 8.8L96 160 48 160c-26.5 0-48 21.5-48 48l0 96c0 26.5 21.5 48 48 48zM367 175c-9.4 9.4-9.4 24.6 0 33.9l47 47-47 47c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l47-47 47 47c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-47-47 47-47c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-47 47-47-47c-9.4-9.4-24.6-9.4-33.9 0z"/></svg>',xmark:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M55.1 73.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L147.2 256 9.9 393.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192.5 301.3 329.9 438.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.8 256 375.1 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192.5 210.7 55.1 73.4z"/></svg>'},regular:{calendar:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M216 64C229.3 64 240 74.7 240 88L240 128L400 128L400 88C400 74.7 410.7 64 424 64C437.3 64 448 74.7 448 88L448 128L480 128C515.3 128 544 156.7 544 192L544 480C544 515.3 515.3 544 480 544L160 544C124.7 544 96 515.3 96 480L96 192C96 156.7 124.7 128 160 128L192 128L192 88C192 74.7 202.7 64 216 64zM216 176L160 176C151.2 176 144 183.2 144 192L144 240L496 240L496 192C496 183.2 488.8 176 480 176L216 176zM144 288L144 480C144 488.8 151.2 496 160 496L480 496C488.8 496 496 488.8 496 480L496 288L144 288z"/></svg>',"circle-question":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M464 256a208 208 0 1 0 -416 0 208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0zm256-80c-17.7 0-32 14.3-32 32 0 13.3-10.7 24-24 24s-24-10.7-24-24c0-44.2 35.8-80 80-80s80 35.8 80 80c0 47.2-36 67.2-56 74.5l0 3.8c0 13.3-10.7 24-24 24s-24-10.7-24-24l0-8.1c0-20.5 14.8-35.2 30.1-40.2 6.4-2.1 13.2-5.5 18.2-10.3 4.3-4.2 7.7-10 7.7-19.6 0-17.7-14.3-32-32-32zM224 368a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/></svg>',"circle-xmark":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M256 48a208 208 0 1 1 0 416 208 208 0 1 1 0-416zm0 464a256 256 0 1 0 0-512 256 256 0 1 0 0 512zM167 167c-9.4 9.4-9.4 24.6 0 33.9l55 55-55 55c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l55-55 55 55c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-55-55 55-55c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-55 55-55-55c-9.4-9.4-24.6-9.4-33.9 0z"/></svg>',clock:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M528 320C528 434.9 434.9 528 320 528C205.1 528 112 434.9 112 320C112 205.1 205.1 112 320 112C434.9 112 528 205.1 528 320zM64 320C64 461.4 178.6 576 320 576C461.4 576 576 461.4 576 320C576 178.6 461.4 64 320 64C178.6 64 64 178.6 64 320zM296 184L296 320C296 328 300 335.5 306.7 340L402.7 404C413.7 411.4 428.6 408.4 436 397.3C443.4 386.2 440.4 371.4 429.3 364L344 307.2L344 184C344 170.7 333.3 160 320 160C306.7 160 296 170.7 296 184z"/></svg>',copy:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M384 336l-192 0c-8.8 0-16-7.2-16-16l0-256c0-8.8 7.2-16 16-16l133.5 0c4.2 0 8.3 1.7 11.3 4.7l58.5 58.5c3 3 4.7 7.1 4.7 11.3L400 320c0 8.8-7.2 16-16 16zM192 384l192 0c35.3 0 64-28.7 64-64l0-197.5c0-17-6.7-33.3-18.7-45.3L370.7 18.7C358.7 6.7 342.5 0 325.5 0L192 0c-35.3 0-64 28.7-64 64l0 256c0 35.3 28.7 64 64 64zM64 128c-35.3 0-64 28.7-64 64L0 448c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-16-48 0 0 16c0 8.8-7.2 16-16 16L64 464c-8.8 0-16-7.2-16-16l0-256c0-8.8 7.2-16 16-16l16 0 0-48-16 0z"/></svg>',eye:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M288 80C222.8 80 169.2 109.6 128.1 147.7 89.6 183.5 63 226 49.4 256 63 286 89.6 328.5 128.1 364.3 169.2 402.4 222.8 432 288 432s118.8-29.6 159.9-67.7C486.4 328.5 513 286 526.6 256 513 226 486.4 183.5 447.9 147.7 406.8 109.6 353.2 80 288 80zM95.4 112.6C142.5 68.8 207.2 32 288 32s145.5 36.8 192.6 80.6c46.8 43.5 78.1 95.4 93 131.1 3.3 7.9 3.3 16.7 0 24.6-14.9 35.7-46.2 87.7-93 131.1-47.1 43.7-111.8 80.6-192.6 80.6S142.5 443.2 95.4 399.4c-46.8-43.5-78.1-95.4-93-131.1-3.3-7.9-3.3-16.7 0-24.6 14.9-35.7 46.2-87.7 93-131.1zM288 336c44.2 0 80-35.8 80-80 0-29.6-16.1-55.5-40-69.3-1.4 59.7-49.6 107.9-109.3 109.3 13.8 23.9 39.7 40 69.3 40zm-79.6-88.4c2.5 .3 5 .4 7.6 .4 35.3 0 64-28.7 64-64 0-2.6-.2-5.1-.4-7.6-37.4 3.9-67.2 33.7-71.1 71.1zm45.6-115c10.8-3 22.2-4.5 33.9-4.5 8.8 0 17.5 .9 25.8 2.6 .3 .1 .5 .1 .8 .2 57.9 12.2 101.4 63.7 101.4 125.2 0 70.7-57.3 128-128 128-61.6 0-113-43.5-125.2-101.4-1.8-8.6-2.8-17.5-2.8-26.6 0-11 1.4-21.8 4-32 .2-.7 .3-1.3 .5-1.9 11.9-43.4 46.1-77.6 89.5-89.5z"/></svg>',"eye-slash":'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M41-24.9c-9.4-9.4-24.6-9.4-33.9 0S-2.3-.3 7 9.1l528 528c9.4 9.4 24.6 9.4 33.9 0s9.4-24.6 0-33.9l-96.4-96.4c2.7-2.4 5.4-4.8 8-7.2 46.8-43.5 78.1-95.4 93-131.1 3.3-7.9 3.3-16.7 0-24.6-14.9-35.7-46.2-87.7-93-131.1-47.1-43.7-111.8-80.6-192.6-80.6-56.8 0-105.6 18.2-146 44.2L41-24.9zM176.9 111.1c32.1-18.9 69.2-31.1 111.1-31.1 65.2 0 118.8 29.6 159.9 67.7 38.5 35.7 65.1 78.3 78.6 108.3-13.6 30-40.2 72.5-78.6 108.3-3.1 2.8-6.2 5.6-9.4 8.4L393.8 328c14-20.5 22.2-45.3 22.2-72 0-70.7-57.3-128-128-128-26.7 0-51.5 8.2-72 22.2l-39.1-39.1zm182 182l-108-108c11.1-5.8 23.7-9.1 37.1-9.1 44.2 0 80 35.8 80 80 0 13.4-3.3 26-9.1 37.1zM103.4 173.2l-34-34c-32.6 36.8-55 75.8-66.9 104.5-3.3 7.9-3.3 16.7 0 24.6 14.9 35.7 46.2 87.7 93 131.1 47.1 43.7 111.8 80.6 192.6 80.6 37.3 0 71.2-7.9 101.5-20.6L352.2 422c-20 6.4-41.4 10-64.2 10-65.2 0-118.8-29.6-159.9-67.7-38.5-35.7-65.1-78.3-78.6-108.3 10.4-23.1 28.6-53.6 54-82.8z"/></svg>',star:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Free 7.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. --><path d="M288.1-32c9 0 17.3 5.1 21.4 13.1L383 125.3 542.9 150.7c8.9 1.4 16.3 7.7 19.1 16.3s.5 18-5.8 24.4L441.7 305.9 467 465.8c1.4 8.9-2.3 17.9-9.6 23.2s-17 6.1-25 2L288.1 417.6 143.8 491c-8 4.1-17.7 3.3-25-2s-11-14.2-9.6-23.2L134.4 305.9 20 191.4c-6.4-6.4-8.6-15.8-5.8-24.4s10.1-14.9 19.1-16.3l159.9-25.4 73.6-144.2c4.1-8 12.4-13.1 21.4-13.1zm0 76.8L230.3 158c-3.5 6.8-10 11.6-17.6 12.8l-125.5 20 89.8 89.9c5.4 5.4 7.9 13.1 6.7 20.7l-19.8 125.5 113.3-57.6c6.8-3.5 14.9-3.5 21.8 0l113.3 57.6-19.8-125.5c-1.2-7.6 1.3-15.3 6.7-20.7l89.8-89.9-125.5-20c-7.6-1.2-14.1-6-17.6-12.8L288.1 44.8z"/></svg>'}},fa={name:"system",resolver:(n,t="classic",e="solid")=>{let a=Qe[e][n]??Qe.regular[n]??Qe.regular["circle-question"];return a?ga(a):""},mutator:n=>{n.hasAttribute("fill")||n.setAttribute("fill","currentColor")}},Li=fa;var va="classic",wa=[Si,Li],ki=new Set;function Ei(n){ki.add(n)}function _i(n){ki.delete(n)}function Pe(n){return wa.find(t=>t.name===n)}function Pi(){return va}var ba=Object.defineProperty,ya=Object.getOwnPropertyDescriptor,b=(n,t,e,i)=>{for(var a=i>1?void 0:i?ya(t,e):t,s=n.length-1,o;s>=0;s--)(o=n[s])&&(a=(i?o(t,e,a):o(a))||a);return i&&a&&ba(t,e,a),a},ce=Symbol(),De=Symbol(),et,tt=new Map,w=class extends A{constructor(){super(...arguments),this.svg=null,this.autoWidth=!1,this.swapOpacity=!1,this.label="",this.library="default",this.rotate=0,this.resolveIcon=async(n,t)=>{let e;if(t?.spriteSheet){this.hasUpdated||await this.updateComplete,this.svg=c`<svg part="svg">
        <use part="use" href="${n}"></use>
      </svg>`,await this.updateComplete;let i=this.shadowRoot.querySelector("[part='svg']");return typeof t.mutator=="function"&&t.mutator(i,this),this.svg}try{if(e=await fetch(n,{mode:"cors"}),!e.ok)return e.status===410?ce:De}catch{return De}try{let i=document.createElement("div");i.innerHTML=await e.text();let a=i.firstElementChild;if(a?.tagName?.toLowerCase()!=="svg")return ce;et||(et=new DOMParser);let o=et.parseFromString(a.outerHTML,"text/html").body.querySelector("svg");return o?(o.part.add("svg"),document.adoptNode(o)):ce}catch{return ce}}}connectedCallback(){super.connectedCallback(),Ei(this)}firstUpdated(n){super.firstUpdated(n),this.hasAttribute("rotate")&&this.style.setProperty("--rotate-angle",`${this.rotate}deg`),this.setIcon()}disconnectedCallback(){super.disconnectedCallback(),_i(this)}async getIconSource(){let n=Pe(this.library),t=this.family||Pi();if(this.name&&n){let e=this.canvas==="auto"||this.autoWidth,i;try{i=await n.resolver(this.name,t,this.variant,e)}catch{i=void 0}return{url:i,fromLibrary:!0}}return{url:this.src,fromLibrary:!1}}handleLabelChange(){typeof this.label=="string"&&this.label.length>0?(this.setAttribute("role","img"),this.setAttribute("aria-label",this.label),this.removeAttribute("aria-hidden")):(this.removeAttribute("role"),this.removeAttribute("aria-label"),this.setAttribute("aria-hidden","true"))}async setIcon(){let{url:n,fromLibrary:t}=await this.getIconSource(),e=t?Pe(this.library):void 0;if(!n){this.svg=null;return}let i=tt.get(n);i||(i=this.resolveIcon(n,e),tt.set(n,i));let a=await i;a===De&&tt.delete(n);let s=await this.getIconSource();if(n===s.url){if(Pt(a)){this.svg=a;return}switch(a){case De:case ce:this.svg=null,this.dispatchEvent(new Ee);break;default:this.svg=a.cloneNode(!0),e?.mutator?.(this.svg,this),this.dispatchEvent(new _e)}}}willUpdate(n){return this.style||this.setStyleProperty("--rotate-angle",`${this.rotate}deg`),super.willUpdate(n)}updated(n){super.updated(n);let t=Pe(this.library);this.hasAttribute("rotate")&&this.style.setProperty("--rotate-angle",`${this.rotate}deg`);let e=this.shadowRoot?.querySelector("svg");e&&t?.mutator?.(e,this)}render(){return this.hasUpdated?this.svg:c`<svg part="svg" width="16" height="16" viewBox="0 0 16 16"></svg>`}};w.css=Ci;b([se()],w.prototype,"svg",2);b([h({reflect:!0})],w.prototype,"name",2);b([h({reflect:!0})],w.prototype,"family",2);b([h({reflect:!0})],w.prototype,"variant",2);b([h({reflect:!0})],w.prototype,"canvas",2);b([h({attribute:"auto-width",type:Boolean,reflect:!0})],w.prototype,"autoWidth",2);b([h({attribute:"swap-opacity",type:Boolean,reflect:!0})],w.prototype,"swapOpacity",2);b([h()],w.prototype,"src",2);b([h()],w.prototype,"label",2);b([h({reflect:!0})],w.prototype,"library",2);b([h({type:Number,reflect:!0})],w.prototype,"rotate",2);b([h({type:String,reflect:!0})],w.prototype,"flip",2);b([h({type:String,reflect:!0})],w.prototype,"animation",2);b([M("label")],w.prototype,"handleLabelChange",1);b([M(["family","name","library","variant","src","autoWidth","canvas","swapOpacity"],{waitUntilFirstUpdate:!0})],w.prototype,"setIcon",1);w=b([z("wa-icon")],w);var Di=v`:host {
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
`;var Ca=Object.defineProperty,xa=Object.getOwnPropertyDescriptor,$a=(n,t,e,i)=>{for(var a=i>1?void 0:i?xa(t,e):t,s=n.length-1,o;s>=0;s--)(o=n[s])&&(a=(i?o(t,e,a):o(a))||a);return i&&a&&Ca(t,e,a),a},it=class extends A{constructor(){super(...arguments),this.localize=new J(this)}render(){return c`
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
    `}};it.css=Di;it=$a([z("wa-spinner")],it);var zi=v`@layer wa-component {
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
`;var Aa=Object.defineProperty,Sa=Object.getOwnPropertyDescriptor,f=(n,t,e,i)=>{for(var a=i>1?void 0:i?Sa(t,e):t,s=n.length-1,o;s>=0;s--)(o=n[s])&&(a=(i?o(t,e,a):o(a))||a);return i&&a&&Aa(t,e,a),a},m=class extends L{constructor(){super(...arguments),this.assumeInteractionOn=["click"],this.hasSlotController=new X(this,"[default]","start","end"),this.localize=new J(this),this.invalid=!1,this.isIconButton=!1,this.title="",this.accessibleLabel="",this.ariaLabel=null,this.variant="neutral",this.appearance="accent",this.size="m",this.withCaret=!1,this.withStart=!1,this.withEnd=!1,this.disabled=!1,this.loading=!1,this.pill=!1,this.type="button",this.iconTag="wa-icon"}static get validators(){return[...super.validators,di()]}handleSizeChange(){ci(this.localName,this.size)}constructLightDOMButton(){let n=document.createElement("button");for(let t of this.attributes)t.name!=="style"&&n.setAttribute(t.name,t.value);return n.type=this.type,n.style.position="absolute !important",n.style.width="0 !important",n.style.height="0 !important",n.style.clipPath="inset(50%) !important",n.style.overflow="hidden !important",n.style.whiteSpace="nowrap !important",this.name&&(n.name=this.name),n.value=this.value||"",n}handleClick(n){if(this.disabled||this.loading){n.preventDefault(),n.stopImmediatePropagation();return}if(this.type!=="submit"&&this.type!=="reset"||!this.getForm())return;let e=this.constructLightDOMButton();this.parentElement?.append(e),e.click(),e.remove()}handleInvalid(){this.dispatchEvent(new W)}handleLabelSlotChange(){let n=this.labelSlot.assignedNodes({flatten:!0}),t=!1,e=!1,i=!1,a=!1,s=this.iconTag==="wa-icon";[...n].forEach(o=>{if(o.nodeType===Node.ELEMENT_NODE){let r=o;o.localName===this.iconTag&&(e=!0,t||(t=o.hasAttribute(s?"label":"aria-label"))),r.localName==="wa-icon"?(e=!0,t||(t=r.label!==void 0)):a=!0}else o.nodeType===Node.TEXT_NODE&&(o.textContent?.trim()||"").length>0&&(i=!0)}),this.isIconButton=e&&!i&&!a,this.customStates.set("icon-button",this.isIconButton),this.isIconButton&&!t&&!this.accessibleLabel&&!this.ariaLabel&&console.warn(`Icon buttons must have a label for screen readers. Add <${this.iconTag} ${s?"label":"aria-label"}="..."> to remove this warning.`,this)}isButton(){return!this.href}isLink(){return!!this.href}handleDisabledChange(){this.customStates.set("disabled",this.disabled),this.updateValidity()}handleHrefChange(){this.customStates.set("link",this.isLink())}handleLoadingChange(){this.customStates.set("loading",this.loading)}setValue(...n){}click(){this.button.click()}focus(n){this.button.focus(n)}blur(){this.button.blur()}render(){let n=this.isLink(),t=n?We`a`:We`button`;return $e`
      <${t}
        part="base button"
        class=${oe({button:!0,caret:this.withCaret,disabled:this.disabled,loading:this.loading,rtl:this.localize.dir()==="rtl","has-label":this.hasSlotController.test("[default]"),"has-start":this.hasSlotController.test("start","withStart"),"has-end":this.hasSlotController.test("end","withEnd"),"is-icon-button":this.isIconButton})}
        ?disabled=${S(n?void 0:this.disabled)}
        type=${S(n?void 0:this.type)}
        title=${this.title}
        name=${S(n?void 0:this.name)}
        value=${S(n?void 0:this.value)}
        href=${S(n?this.href:void 0)}
        target=${S(n?this.target:void 0)}
        download=${S(n?this.download:void 0)}
        rel=${S(n&&this.rel?this.rel:void 0)}
        role=${S(n?void 0:"button")}
        aria-disabled=${S(n&&this.disabled?"true":void 0)}
        aria-label=${S(this.accessibleLabel||this.ariaLabel||void 0)}
        aria-busy=${this.loading?"true":"false"}
        tabindex=${this.disabled?"-1":"0"}
        @invalid=${this.isButton()?this.handleInvalid:null}
        @click=${this.handleClick}
      >
        <slot name="start" part="start" class="start"></slot>
        <slot part="label" class="label" @slotchange=${this.handleLabelSlotChange}></slot>
        <slot name="end" part="end" class="end"></slot>
        ${this.withCaret?$e`
                <wa-icon part="caret" class="caret" library="system" name="chevron-down" variant="solid"></wa-icon>
              `:""}
        ${this.loading?$e`<wa-spinner part="spinner"></wa-spinner>`:""}
      </${t}>
    `}};m.shadowRootOptions={...L.shadowRootOptions,delegatesFocus:!0};m.css=[zi,fi,Le];f([je(".button")],m.prototype,"button",2);f([je("slot:not([name])")],m.prototype,"labelSlot",2);f([se()],m.prototype,"invalid",2);f([se()],m.prototype,"isIconButton",2);f([h()],m.prototype,"title",2);f([h({attribute:"accessible-label"})],m.prototype,"accessibleLabel",2);f([h({attribute:"aria-label"})],m.prototype,"ariaLabel",2);f([h({reflect:!0})],m.prototype,"variant",2);f([h({reflect:!0})],m.prototype,"appearance",2);f([h({reflect:!0})],m.prototype,"size",2);f([M("size")],m.prototype,"handleSizeChange",1);f([h({attribute:"with-caret",type:Boolean,reflect:!0})],m.prototype,"withCaret",2);f([h({attribute:"with-start",type:Boolean})],m.prototype,"withStart",2);f([h({attribute:"with-end",type:Boolean})],m.prototype,"withEnd",2);f([h({type:Boolean})],m.prototype,"disabled",2);f([h({type:Boolean,reflect:!0})],m.prototype,"loading",2);f([h({type:Boolean,reflect:!0})],m.prototype,"pill",2);f([h()],m.prototype,"type",2);f([h({reflect:!0})],m.prototype,"name",2);f([h({reflect:!0})],m.prototype,"value",2);f([h({reflect:!0})],m.prototype,"href",2);f([h()],m.prototype,"target",2);f([h()],m.prototype,"rel",2);f([h()],m.prototype,"download",2);f([h({attribute:"formaction"})],m.prototype,"formAction",2);f([h({attribute:"formenctype"})],m.prototype,"formEnctype",2);f([h({attribute:"formmethod"})],m.prototype,"formMethod",2);f([h({attribute:"formnovalidate",type:Boolean})],m.prototype,"formNoValidate",2);f([h({attribute:"formtarget"})],m.prototype,"formTarget",2);f([h()],m.prototype,"iconTag",2);f([M("disabled",{waitUntilFirstUpdate:!0})],m.prototype,"handleDisabledChange",1);f([M("href")],m.prototype,"handleHrefChange",1);f([M("loading",{waitUntilFirstUpdate:!0})],m.prototype,"handleLoadingChange",1);m=f([z("wa-button")],m);m.disableWarning?.("change-in-update");var at=class extends m{constructor(){super(...arguments);this.appearance="outlined";this.expanded=void 0;this.pressed=void 0;this.busy=!1}static{this.properties={expanded:{type:Boolean},pressed:{type:Boolean},busy:{type:Boolean,reflect:!0}}}updated(e){super.updated(e),this.expanded===void 0?this.button.removeAttribute("aria-expanded"):this.button.setAttribute("aria-expanded",String(this.expanded)),this.pressed===void 0?this.button.removeAttribute("aria-pressed"):this.button.setAttribute("aria-pressed",String(this.pressed)),this.busy?this.button.setAttribute("aria-busy","true"):this.button.removeAttribute("aria-busy")}render(){return c`
      ${super.render()}
      ${this.busy?c`<svg class="busy-outline" aria-hidden="true">
              <rect pathLength="100"></rect>
            </svg>`:p}
    `}static get styles(){return[m.styles,v`
        :host {
          position: relative;
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
        :host([busy]) .button {
          border-color: transparent;
        }
        .busy-outline {
          position: absolute;
          inset: 0;
          inline-size: 100%;
          block-size: 100%;
          pointer-events: none;
        }
        .busy-outline rect {
          x: 1px;
          y: 1px;
          width: calc(100% - 2px);
          height: calc(100% - 2px);
          rx: var(--axis-radius-control);
          fill: none;
          stroke: var(--axis-color-primary);
          stroke-width: 2px;
          stroke-dasharray: 3 2;
          animation: busy-dashes 650ms linear infinite;
        }
        @keyframes busy-dashes {
          to {
            stroke-dashoffset: -5;
          }
        }
        @media (prefers-reduced-motion: reduce) {
          .busy-outline rect {
            animation: none;
          }
        }
      `]}};customElements.define("axis-button",at);var Mi=v`:host {
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
`;var La=Object.defineProperty,ka=Object.getOwnPropertyDescriptor,F=(n,t,e,i)=>{for(var a=i>1?void 0:i?ka(t,e):t,s=n.length-1,o;s>=0;s--)(o=n[s])&&(a=(i?o(t,e,a):o(a))||a);return i&&a&&La(t,e,a),a},$=class extends A{constructor(){super(...arguments),this.hasSlotController=new X(this,"footer","header","media","header-actions","footer-actions","actions"),this.appearance="outlined",this.withHeader=!1,this.withMedia=!1,this.withFooter=!1,this.withHeaderActions=!1,this.withFooterActions=!1,this.orientation="vertical"}willUpdate(n){this.withHeader=this.hasSlotController.test("header","withHeader"),this.withMedia=this.hasSlotController.test("media","withMedia"),this.withFooter=this.hasSlotController.test("footer","withFooter"),super.willUpdate(n)}render(){if(this.orientation==="horizontal")return c`
        <slot name="media" part="media" class="media"></slot>
        <div part="body" class="body"><slot></slot></div>
        <slot name="actions" part="actions" class="actions"></slot>
      `;let n=this.hasSlotController.test("header-actions","withHeaderActions"),t=this.hasSlotController.test("footer-actions","withFooterActions");return c`
      <slot name="media" part="media" class="media"></slot>

      <div
        part="header"
        class=${oe({header:!0,"has-actions":n})}
      >
        <slot name="header"></slot>
        <slot name="header-actions"></slot>
      </div>

      <div part="body" class="body"><slot></slot></div>

      <div
        part="footer"
        class=${oe({footer:!0,"has-actions":t})}
      >
        <slot name="footer"></slot>
        <slot name="footer-actions"></slot>
      </div>
    `}};$.css=[Le,Mi];F([h({reflect:!0})],$.prototype,"appearance",2);F([h({attribute:"with-header",type:Boolean,reflect:!0})],$.prototype,"withHeader",2);F([h({attribute:"with-media",type:Boolean,reflect:!0})],$.prototype,"withMedia",2);F([h({attribute:"with-footer",type:Boolean,reflect:!0})],$.prototype,"withFooter",2);F([h({attribute:"with-header-actions",type:Boolean,reflect:!0})],$.prototype,"withHeaderActions",2);F([h({attribute:"with-footer-actions",type:Boolean,reflect:!0})],$.prototype,"withFooterActions",2);F([h({reflect:!0})],$.prototype,"orientation",2);$=F([z("wa-card")],$);$.disableWarning?.("change-in-update");var nt=class extends ${static get styles(){return[$.styles,v`
        :host {
          --spacing: var(--axis-space-4);
          --wa-panel-border-radius: var(--axis-radius-card);
          --wa-panel-border-width: var(--axis-border-width);
          --wa-panel-border-style: solid;
          --wa-shadow-s: none;
          min-inline-size: 0;
        }
      `]}};customElements.define("axis-card",nt);var st=class extends x{constructor(){super(...arguments);this.device=null;this.health=null;this.loading=!1}static{this.properties={device:{attribute:!1},health:{attribute:!1},loading:{type:Boolean}}}static{this.styles=j}render(){if(!this.device)return p;let e=this.health?.serial===this.device.serial;return c`
      <axis-card>
        <h3>Device health</h3>
        ${!this.loading&&!this.health?c`<p>No live health data available. Check the connection and select Health again to retry.</p>`:p}
        ${this.health?c`
                ${e?p:c`<p class="warning">Warning: the connected device serial does not match the saved target.</p>`}
                <dl>
                  ${e?c`<dt>Serial</dt>
                          <dd>${this.health.serial}</dd>`:c`<dt>Saved serial</dt>
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
              `:p}
      </axis-card>
    `}};customElements.define("axis-device-health",st);function B(n){let t=n?.trim().toLowerCase().replace(/\*+$/,"").replace(/[:-]/g,"");return t&&/^[0-9a-f]{12}$/.test(t)?t:void 0}function Fi(n,t,e,i,a=!1){let s=[n?t:"",e,i].filter(Boolean).join(" \u2014 ");return c`
    <span class="device-info">
      <span class="device-heading">
        <span class="device-name">${n||t}</span>
        ${a?c`<span class="warning">Discovered</span>`:p}
      </span>
      ${s?c`<span class="device-meta">${s}</span>`:p}
    </span>
  `}function Ea(n,t){let e=B(n.macaddress);return t.some(i=>i.serial===n.serial||e!==void 0&&(e===B(i.serial)||e===B(i.discovery?.macaddress)))}var ot=class extends x{constructor(){super(...arguments);this.devices=[];this.discovery=null;this.selected="";this.connected=!1;this.warning=""}static{this.properties={devices:{attribute:!1},discovery:{attribute:!1},selected:{},connected:{type:Boolean},warning:{}}}static{this.styles=[j,v`
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
      .device-info {
        display: grid;
        gap: var(--axis-space-1);
        min-inline-size: 0;
      }
      .device-heading {
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        gap: var(--axis-space-2);
      }
      .device-meta {
        font-size: 0.875rem;
        font-weight: 400;
        opacity: 0.9;
      }
      .device-heading .warning {
        font-size: 0.75rem;
      }
      .discovered {
        --wa-color-neutral-border-quiet: var(--axis-color-warning);
      }
      .discovered::part(base) {
        border-color: var(--axis-color-warning);
      }
      .scan-control {
        position: relative;
        display: flex;
        justify-content: flex-end;
        margin-block-start: var(--axis-space-2);
      }
      .scan-control .failed::part(base) {
        border-color: var(--axis-color-danger);
      }
      .scan-status {
        position: absolute;
        inline-size: 1px;
        block-size: 1px;
        overflow: hidden;
        clip-path: inset(50%);
        white-space: nowrap;
      }
    `]}render(){let e=this.discovery,i=e?.devices??[],a=i.filter(d=>!Ea(d,this.devices)),s=e?.status==="scanning",o=e?.status==="error",r=s?"Discovering devices\u2026":o?"Retry discovery \xB7 Failed":e?.status==="complete"?`Discover devices \xB7 ${a.length?`${a.length} new`:"No new devices"}`:"Discover devices",l=o?e.message:e?.status==="complete"&&!a.length?i.length?"All discovered devices are already saved.":"No Axis devices found.":e?r:"";return c`
      <axis-card>
        ${this.devices.length||a.length?c`
                <ul class="device-rows" role="list" aria-label="Devices">
                  ${this.devices.map(d=>c`
                      <li>
                        <axis-button
                          variant=${d.serial===this.selected?"brand":"neutral"}
                          appearance=${d.serial===this.selected?"accent":"outlined"}
                          .pressed=${d.serial===this.selected}
                          ?disabled=${!this.connected}
                          @click=${()=>this.dispatchEvent(new CustomEvent("axis-select",{detail:d.serial}))}
                        >
                          ${Fi(H(d),d.host,d.discovery?.macaddress||B(d.serial)?.match(/../g)?.join(":"))}
                        </axis-button>
                      </li>
                    `)}
                  ${a.map(d=>c`
                      <li>
                        <axis-button
                          class="discovered"
                          ?disabled=${!this.connected}
                          @click=${()=>this.dispatchEvent(new CustomEvent("axis-register",{detail:d}))}
                        >
                          ${Fi(d.name,d.host,d.macaddress,d.model,!0)}
                        </axis-button>
                      </li>
                    `)}
                </ul>
              `:p}
        <div class="scan-control">
          <axis-button
            class=${o?"failed":""}
            .busy=${s}
            ?disabled=${!this.connected}
            aria-disabled=${s?"true":"false"}
            title=${o?e.message:""}
            @click=${()=>{this.connected&&!s&&this.dispatchEvent(new Event("axis-scan"))}}
            >${r}</axis-button
          >
          <span class="scan-status" role="status">${l}</span>
        </div>
        ${this.warning?c`<p class="warning" role="status">${this.warning}</p>`:p}
        ${this.devices.length===0?c`<p>No saved devices. Use Discover devices to find devices on the local network.</p>`:""}
      </axis-card>
    `}};customElements.define("axis-device-list",ot);var _a=["Health","Applications","APIs","Interfaces"],Pa={connecting:"Connecting to Axis\u2026",connected:"Connected to Axis",reconnecting:"Reconnecting to Axis\u2026",denied:"Access link rejected","link-required":"Access link required"},rt=n=>n==="https"?443:80;function Da(n,t){let e=Number(n.get("port")),i=String(n.get("web_proto")??"");return t?.web_proto===i&&t.port===e?e:e===rt(i)?0:e}function ze(n,t){let e=i=>String(n.get(i)??"");return{host:e("host"),port:Da(n,t),username:e("username"),password:e("password"),web_proto:e("web_proto"),verify_ssl:n.has("verify_ssl")}}function za(n){try{let t=new URL(n);if((t.protocol==="https:"||t.protocol==="http:")&&!t.username&&!t.password)return t}catch{return null}return null}var lt=class extends x{constructor(){super(...arguments);this.status="connecting";this.devices=[];this.discovery=null;this.selected="";this.deviceView="Health";this.viewData={};this.capabilities=new Map;this.selectedInterface=null;this.error="";this.loading=null;this.registration=null;this.saving=!1;this.saveError="";this.settings=null;this.settingsPending=!1;this.settingsError="";this.connectionEdited=!1;this.connectionTest=null;this.serverSettingsOpen=!1;this.serverSettings=null;this.serverPending=!1;this.serverError="";this.serverAutomatic=!0;this.serverSelection=[];this.acapFolder="";this.folderBrowserOpen=!1;this.folderBrowser=null;this.folderBrowserPending=!1;this.folderBrowserError="";this.folderBrowserRequest=0;this.acapCatalog=null;this.acapCatalogError="";this.discoveryWarning="";this.restartConfirming=!1;this.restartPending=!1;this.restartMessage="";this.restartFailed=!1;this.applicationsOpen=!1;this.applicationSupported=null;this.applicationSupportError="";this.applicationSupportRequest=0;this.applicationSupportPending=null;this.applications=null;this.applicationViews=new Map;this.applicationsStale=!1;this.selectedApplication=null;this.applicationLoading=!1;this.applicationPending=!1;this.applicationConfirmation=null;this.applicationUpdates=[];this.applicationUpdatesError="";this.updateApp=null;this.expandedUpdates=!1;this.updateConfirmation=null;this.updateRecovery=null;this.updatesRequest=0;this.installationOpen=!1;this.installationFile=null;this.installationError="";this.installationDragging=!1;this.installCandidates=null;this.installCandidatesLoading=!1;this.installCandidatesError="";this.installAppsExpanded=!1;this.installExpandedApp="";this.installCandidatesExpanded=!1;this.installCandidate=null;this.installDetail=null;this.installCandidatesRequest=0;this.applicationMessage="";this.applicationFailed=!1;this.applicationArchitecture="";this.applicationSdks="";this.applicationPolicy=null;this.applicationPolicyError="";this.licenseSelection=null;this.licenseOpen=!1;this.licenseAppName="";this.licenseFile=null;this.licenseError="";this.licenseDragging=!1;this.architectureRequest=0;this.applicationInfoRequest=0;this.applicationPolicyRequest=0;this.operation=0;this.refreshId=0;this.backdropPressed=!1;this.portDrafts=new WeakMap;this.connection=new xe(e=>this.connectionChanged(e));this.preventInstallationDrop=e=>{(this.installationOpen||this.licenseOpen)&&e.preventDefault()};this.openAccessLink=()=>{let e=location.hash.slice(1)||sessionStorage.getItem("axis-token")||"";if(location.hash&&(sessionStorage.setItem("axis-token",e),history.replaceState(null,"",location.pathname)),!e){this.connection.disconnect(),this.status="link-required",this.error="Open the private URL printed when the server starts.";return}this.connection.connect(e)};this.alignDeviceDialog=()=>{let e=this.renderRoot.querySelector("dialog"),i=this.renderRoot.querySelector("axis-device-list");if(e&&i){let a=i.getBoundingClientRect().top+window.scrollY;e.style.setProperty("--axis-dialog-top",`${a}px`)}}}static{this.properties={status:{state:!0},devices:{state:!0},discovery:{state:!0},selected:{state:!0},deviceView:{state:!0},viewData:{state:!0},selectedInterface:{state:!0},error:{state:!0},loading:{state:!0},registration:{state:!0},saving:{state:!0},saveError:{state:!0},settings:{state:!0},settingsPending:{state:!0},settingsError:{state:!0},connectionEdited:{state:!0},connectionTest:{state:!0},serverSettingsOpen:{state:!0},serverSettings:{state:!0},serverPending:{state:!0},serverError:{state:!0},serverAutomatic:{state:!0},serverSelection:{state:!0},acapFolder:{state:!0},folderBrowserOpen:{state:!0},folderBrowser:{state:!0},folderBrowserPending:{state:!0},folderBrowserError:{state:!0},acapCatalog:{state:!0},acapCatalogError:{state:!0},discoveryWarning:{state:!0},restartConfirming:{state:!0},restartPending:{state:!0},restartMessage:{state:!0},restartFailed:{state:!0},applicationsOpen:{state:!0},applicationSupported:{state:!0},applicationSupportError:{state:!0},applications:{state:!0},applicationsStale:{state:!0},selectedApplication:{state:!0},applicationLoading:{state:!0},applicationPending:{state:!0},applicationConfirmation:{state:!0},applicationUpdates:{state:!0},applicationUpdatesError:{state:!0},updateApp:{state:!0},expandedUpdates:{state:!0},updateConfirmation:{state:!0},updateRecovery:{state:!0},installationOpen:{state:!0},installationFile:{state:!0},installationError:{state:!0},installationDragging:{state:!0},installCandidates:{state:!0},installCandidatesLoading:{state:!0},installCandidatesError:{state:!0},installAppsExpanded:{state:!0},installExpandedApp:{state:!0},installCandidatesExpanded:{state:!0},installCandidate:{state:!0},installDetail:{state:!0},applicationMessage:{state:!0},applicationFailed:{state:!0},applicationArchitecture:{state:!0},applicationSdks:{state:!0},applicationPolicy:{state:!0},applicationPolicyError:{state:!0},licenseSelection:{state:!0},licenseOpen:{state:!0},licenseAppName:{state:!0},licenseFile:{state:!0},licenseError:{state:!0},licenseDragging:{state:!0}}}static{this.styles=[j,v`
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
      .app-heading {
        display: flex;
        margin-block-end: var(--axis-space-4);
      }
      .app-heading h1 {
        margin-block-end: 0;
      }
      .connection-heading {
        display: inline-block;
        min-inline-size: 0;
        max-inline-size: 100%;
      }
      .connection-status {
        display: block;
        block-size: 3px;
        margin-block-start: var(--axis-space-1);
        border-radius: var(--axis-radius-control);
        background-color: var(--axis-color-danger);
      }
      .connection-status[data-state="connected"] {
        background-color: var(--axis-color-success);
      }
      .connection-status:is(
        [data-state="connecting"],
        [data-state="reconnecting"]
      ) {
        background-color: light-dark(#a94c00, #ffd08a);
        animation: connection-pulse 1.6s ease-in-out infinite alternate;
      }
      @keyframes connection-pulse {
        to {
          opacity: 0.55;
        }
      }
      @media (prefers-reduced-motion: reduce) {
        .connection-status:is(
          [data-state="connecting"],
          [data-state="reconnecting"]
        ) {
          animation: none;
        }
      }
      .panels {
        display: grid;
        gap: var(--axis-space-4);
      }
      dialog {
        box-sizing: border-box;
        inline-size: min(
          var(--axis-content-width),
          calc(100% - var(--axis-space-4))
        );
        max-inline-size: none;
        inset-block: var(--axis-dialog-top) auto;
        margin-block: 0;
        max-block-size: calc(
          100dvh - var(--axis-dialog-top) - var(--axis-space-2)
        );
        padding: 0;
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-card);
        background: var(--axis-color-background);
        color: var(--axis-color-text);
        overflow: hidden;
      }
      dialog[open] {
        display: grid;
        grid-template-rows: auto minmax(0, 1fr);
      }
      dialog::backdrop {
        background: rgb(0 0 0 / 55%);
      }
      dialog.installation-dialog,
      dialog.application-dialog,
      dialog.update-dialog,
      dialog.package-dialog,
      dialog.license-dialog {
        inline-size: min(36rem, calc(100% - var(--axis-space-4)));
        inset: 0;
        margin: auto;
        max-block-size: calc(100dvh - var(--axis-space-4));
      }
      .license-dialog select {
        box-sizing: border-box;
        inline-size: 100%;
        min-inline-size: 0;
        max-inline-size: 100%;
      }
      .installation-drop {
        display: grid;
        justify-items: center;
        gap: var(--axis-space-3);
        padding: var(--axis-space-4);
        border: 2px dashed var(--axis-color-border);
        border-radius: var(--axis-radius-card);
        background: var(--axis-color-surface);
        text-align: center;
      }
      .installation-drop[data-dragging] {
        border-color: var(--axis-color-primary);
        background: var(--axis-color-surface-muted);
      }
      .installation-drop p {
        margin: 0;
        overflow-wrap: anywhere;
      }
      .installation-selection {
        box-sizing: border-box;
        inline-size: 100%;
        padding: var(--axis-space-3);
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-control);
        background: var(--axis-color-surface-muted);
        text-align: start;
      }
      .installation-selection p + p {
        margin-block-start: var(--axis-space-2);
      }
      .folder-browser {
        margin-block: var(--axis-space-3);
        padding: var(--axis-space-3);
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-card);
      }
      .folder-browser p {
        overflow-wrap: anywhere;
      }
      .folder-list {
        display: grid;
        justify-items: start;
        max-block-size: 15rem;
        overflow: auto;
        gap: var(--axis-space-1);
      }
      .dialog-header {
        padding: var(--axis-space-4);
        border-block-end: var(--axis-border-width) solid
          var(--axis-color-border);
      }
      .dialog-heading {
        flex-wrap: nowrap;
        align-items: start;
      }
      .dialog-header h2 {
        margin: 0;
        min-inline-size: 0;
        overflow-wrap: anywhere;
      }
      .dialog-controls {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: var(--axis-space-2);
      }
      .dialog-controls button:not(:disabled),
      .server-settings-trigger:not(:disabled) {
        cursor: pointer;
      }
      .dialog-controls button:not(:disabled):hover,
      .server-settings-trigger:not(:disabled):hover {
        background: var(--axis-color-surface-muted);
      }
      .server-interfaces label {
        display: flex;
        align-items: baseline;
        gap: var(--axis-space-2);
      }
      .server-interface-detail {
        font-size: 0.875rem;
        font-weight: 400;
      }
      .application-list {
        display: grid;
        gap: var(--axis-space-2);
        list-style: none;
        margin-block: var(--axis-space-2) 0;
        padding: 0;
      }
      .application-list li {
        min-inline-size: 0;
      }
      .application-list axis-button {
        display: block;
        inline-size: 100%;
      }
      .application-list axis-button::part(base) {
        justify-content: flex-start;
        text-align: start;
      }
      .application-info {
        display: grid;
        gap: var(--axis-space-1);
        min-inline-size: 0;
      }
      .install-versions {
        margin-block-start: var(--axis-space-2);
        margin-inline-start: var(--axis-space-3);
        padding-inline-start: var(--axis-space-3);
        border-inline-start: 2px solid var(--axis-color-primary);
      }
      .application-meta {
        font-size: 0.875rem;
        font-weight: 400;
        opacity: 0.9;
      }
      .application-update {
        color: var(--axis-color-success);
      }
      .application-heading {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: baseline;
        gap: var(--axis-space-3);
      }
      .application-heading h4 {
        margin: 0;
        overflow-wrap: anywhere;
      }
      .policy-toggle {
        display: inline-flex;
        align-items: center;
        gap: var(--axis-space-2);
      }
      .policy-toggle input {
        appearance: none;
        box-sizing: border-box;
        inline-size: 2.75rem;
        block-size: 1.5rem;
        border: 1px solid var(--axis-color-border);
        border-radius: 1rem;
        background: var(--axis-color-surface-muted);
        cursor: pointer;
      }
      .policy-toggle input::before {
        content: "";
        display: block;
        inline-size: 1rem;
        block-size: 1rem;
        margin: 0.1875rem;
        border-radius: 50%;
        background: var(--axis-color-text);
      }
      .policy-toggle input:checked {
        background: var(--axis-color-primary);
      }
      .policy-toggle input:checked::before {
        transform: translateX(1.25rem);
        background: var(--axis-color-on-primary);
      }
      .policy-toggle input:focus-visible {
        outline: var(--axis-focus-ring);
        outline-offset: 2px;
      }
      .policy-toggle input:disabled {
        cursor: not-allowed;
        opacity: 0.6;
      }
      .application-status {
        font-weight: var(--axis-font-weight-medium);
        color: var(--axis-color-warning);
      }
      .application-status[data-status="Running"] {
        color: var(--axis-color-success);
      }
      .update-warning {
        color: var(--axis-color-warning);
      }
      .application-dialog dl {
        margin-block: var(--axis-space-2);
      }
      .device-views axis-button::part(base) {
        border-color: transparent;
        background: transparent;
      }
      .device-views axis-button.active::part(base) {
        border-color: var(--axis-color-border);
        background: var(--axis-color-surface-muted);
        color: var(--axis-color-primary);
      }
      .settings-form input::placeholder {
        color: color-mix(
          in srgb,
          var(--axis-color-text) 70%,
          var(--axis-color-surface)
        );
        opacity: 1;
      }
      .settings-form fieldset + fieldset {
        margin-block-start: var(--axis-space-4);
      }
      .settings-form legend {
        font-weight: var(--axis-font-weight-medium);
        margin-block-end: var(--axis-space-2);
      }
      .dialog-content {
        overflow: auto;
        overscroll-behavior: contain;
        padding: var(--axis-space-4);
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
      select,
      button {
        font: inherit;
        color: inherit;
      }
      input:not([type="checkbox"]),
      select,
      button {
        min-block-size: var(--axis-control-height);
        padding-inline: var(--axis-space-3);
        border: var(--axis-border-width) solid var(--axis-color-border);
        border-radius: var(--axis-radius-control);
        background: var(--axis-color-surface);
      }
      .form-status,
      .connection-status [role="status"] {
        position: absolute;
        clip-path: inset(50%);
        inline-size: 1px;
        block-size: 1px;
        overflow: hidden;
        white-space: nowrap;
      }
    `]}connectedCallback(){super.connectedCallback(),window.addEventListener("hashchange",this.openAccessLink),window.addEventListener("resize",this.alignDeviceDialog),window.addEventListener("dragover",this.preventInstallationDrop),window.addEventListener("drop",this.preventInstallationDrop),this.openAccessLink()}disconnectedCallback(){window.removeEventListener("hashchange",this.openAccessLink),window.removeEventListener("resize",this.alignDeviceDialog),window.removeEventListener("dragover",this.preventInstallationDrop),window.removeEventListener("drop",this.preventInstallationDrop),this.connection.disconnect(),super.disconnectedCallback()}updated(){let e=this.renderRoot.querySelector("dialog");if(!e)return;this.serverSettingsOpen||this.registration!==null||this.selected!==""?(this.alignDeviceDialog(),e.open||e.showModal()):e.open&&(e.close(),this.shadowRoot?.activeElement||this.renderRoot.querySelector("h1")?.focus());let a=this.renderRoot.querySelector(".installation-dialog");a&&(this.installationOpen&&!a.open?a.showModal():!this.installationOpen&&a.open&&a.close());let s=this.renderRoot.querySelector(".package-dialog");s&&(this.installDetail&&this.installationOpen&&!s.open?s.showModal():(!this.installDetail||!this.installationOpen)&&s.open&&s.close());let o=this.renderRoot.querySelector(".application-dialog");o&&(this.selectedApplication&&!o.open?o.showModal():!this.selectedApplication&&o.open&&o.close());let r=this.renderRoot.querySelector(".update-dialog");r&&(this.updateApp&&!r.open?r.showModal():!this.updateApp&&r.open&&r.close());let l=this.renderRoot.querySelector(".license-dialog");l&&(this.licenseOpen&&!l.open?l.showModal():!this.licenseOpen&&l.open&&l.close())}dismissDevice(e){if(e?.preventDefault(),this.saving||this.settingsPending||this.serverPending||this.restartPending||this.applicationPending)return;let i=this.serverSettingsOpen;++this.operation,this.registration=null,this.serverSettingsOpen=!1,this.settings=null,this.connectionTest=null,this.selected="",this.viewData={},this.selectedInterface=null,this.loading=null,this.applicationLoading=!1,this.error="",this.restartConfirming=!1,this.restartMessage="",this.applicationsOpen=!1,this.resetApplicationSupport(),this.applications=null,this.applicationsStale=!1,this.selectedApplication=null,this.clearApplicationUpdates(),++this.architectureRequest,++this.applicationInfoRequest,++this.applicationPolicyRequest,this.applicationArchitecture="",this.applicationSdks="",this.applicationPolicy=null,this.licenseSelection=null,this.licenseOpen=!1,this.licenseAppName="",this.licenseFile=null,this.licenseError="",this.licenseDragging=!1,this.applicationConfirmation=null,this.installationOpen=!1,this.installationFile=null,this.installationError="",this.installationDragging=!1,this.applicationMessage="",i&&this.updateComplete.then(()=>this.renderRoot.querySelector(".server-settings-trigger")?.focus())}connectionChanged(e){if(!(this.status===e&&e==="reconnecting")){if(this.status=e,this.error=e==="denied"?"Open the private URL printed by the running server.":"",e==="connected"){if(this.refreshDevices(),this.scanLocalNetwork(),this.applicationsOpen&&this.selected){let i=this.selected;this.ensureApplicationSupport(i).then(()=>{!this.applicationsOpen||this.selected!==i||this.applicationSupported!==!0||this.applicationPending||(this.loadApplicationInfo(i),this.updateRecovery?this.refreshUpdateRecovery(i):this.loadApplications(i),this.installationOpen&&(this.loadArchitecture(i),this.loadApplicationSdks(i),this.loadInstallCandidates(i)))})}return}++this.operation,++this.refreshId,this.capabilities.clear(),this.applicationViews.clear(),this.applicationsStale=this.applications!==null,this.resetApplicationSupport(),this.discovery&&(this.discovery={status:"interrupted",devices:this.discovery.devices}),this.registration=null,this.serverSettingsOpen=!1,this.serverPending=!1,this.settings=null,this.connectionTest=null,this.settingsPending=!1,this.saving=!1,this.saveError="",e!=="reconnecting"&&(this.viewData={},this.selectedInterface=null),this.loading=null,this.applicationLoading=!1,this.applicationConfirmation=null,++this.architectureRequest,++this.applicationInfoRequest,++this.applicationPolicyRequest,this.updateRecovery?(this.applicationsStale=!0,this.updateRecovery={...this.updateRecovery,status:"unavailable",confirming:!1}):(!this.applicationPending||!this.updateConfirmation)&&this.clearApplicationUpdates(),++this.installCandidatesRequest,this.installDetail=null,this.installCandidatesLoading=!1,this.installCandidate=null,this.installationOpen&&(this.installCandidatesError="Connection lost. Reconnect to check catalog packages.")}}async refreshDevices(){let e=++this.refreshId;try{let i=await Ft(this.connection);if(this.refreshId!==e)return;this.devices=i;for(let a of this.capabilities.keys())i.some(s=>s.serial===a)||this.capabilities.delete(a);for(let a of this.applicationViews.keys())i.some(s=>s.serial===a)||this.applicationViews.delete(a);this.error="",this.selected&&this.devices.some(a=>a.serial===this.selected)?!this.applicationPending&&!this.applicationsOpen&&await this.showDeviceView(this.selected,this.deviceView):this.applicationPending||(++this.operation,this.selected="",this.viewData={},this.selectedInterface=null,this.loading=null)}catch(i){this.refreshId===e&&(this.error=i.message)}}async scanLocalNetwork(){if(this.status!=="connected"||this.saving||this.discovery?.status==="scanning")return;this.registration=null;let e={status:"scanning",devices:this.discovery?.devices??[]};this.discovery=e,this.discoveryWarning="";try{let i=await Rt(this.connection,a=>{if(this.discovery!==e)return;let s=new Map(e.devices.map(o=>[o.host,o]));s.set(a.host,a),e={status:"scanning",devices:[...s.values()]},this.discovery=e},a=>{this.discovery===e&&(this.discoveryWarning=a)});if(this.discovery===e){let a=new Map(i.map(o=>[o.host,o])),s=e.devices.flatMap(({host:o})=>{let r=a.get(o);return a.delete(o),r?[r]:[]});this.discovery={status:"complete",devices:[...s,...a.values()]}}}catch(i){this.discovery===e&&(this.discovery={status:"error",devices:e.devices,message:i.message})}}openRegistration(e){this.connectionTest=null,this.registration=e,this.saveError="",this.selected="",++this.operation}registrationBlock(e){if(this.discovery?.status==="scanning")return"Wait for discovery to finish before testing the connection.";let i=B(e.macaddress)??e.macaddress;return this.discovery?.status==="complete"&&this.discovery.devices.some(s=>s.host===e.host&&(B(s.macaddress)??s.macaddress)===i)?"":"This device was not confirmed. Close this form and run discovery again."}async submitRegistration(e){e.preventDefault();let i=e.currentTarget,a=this.registration;if(!(i instanceof HTMLFormElement)||!a||this.registrationBlock(a)||this.saving||this.connectionTest?.pending)return;let s=new FormData(i),o=ze(s);if(!this.connectionVerified(o))return;let r=i.querySelector('input[name="password"]');r&&(r.value=""),this.connectionTest=null,this.saving=!0,this.saveError="";try{let l=await Tt(this.connection,{...o,host:a.host,alias:String(s.get("alias")??"")});if(this.registration!==a)return;this.registration=null,this.saving=!1,this.selected=l,this.deviceView="Health";let d=this.renderRoot.querySelector(".dialog-content");d&&(d.scrollTop=0),await this.refreshDevices()}catch(l){this.registration===a&&(this.saveError=l.message)}finally{this.registration===a&&(this.saving=!1)}}renderRegistration(e){let i=this.registrationBlock(e);return zt(e.host,c`
        <axis-card>
          <h3>Save discovered device</h3>
          <p>
            ${i&&this.discovery?.status!=="scanning"?i:"Enter the device credentials to read its identity and save it locally."}
          </p>
          ${this.renderSettingsForm(e,i)}
        </axis-card>
      `)}async showDeviceView(e,i,a=!1){if(!this.applicationPending){if(i==="Applications")return this.openApplications(e,a);if(this.applicationsOpen&&this.closeApplications(!1),this.deviceView!==i){let s=this.renderRoot.querySelector(".dialog-content");s&&(s.scrollTop=0)}if(this.selected=e,this.deviceView=i,!a&&(i==="Health"&&this.viewData.health||i==="APIs"&&this.viewData.apis||i==="Interfaces"&&this.viewData.interfaces)){this.useCachedView();return}return i==="Health"?this.browse(()=>Ut(this.connection,e),s=>{let o=this.viewData.health,r=s.firmware_version.trim(),l=s.serial===e&&!!r&&!["unknown","<unknown>","none","n/a"].includes(r.toLowerCase()),d=this.capabilities.get(e);(!l||d&&d.firmware!==s.firmware_version)&&(this.capabilities.delete(e),this.applicationViews.delete(e),d=void 0,this.resetApplicationSupport()),(!l||o&&(o.serial!==s.serial||o.firmware_version!==s.firmware_version))&&(this.viewData={},this.resetApplicationSupport()),l&&!d&&(d={firmware:s.firmware_version},this.capabilities.set(e,d)),d?.applicationSupported!==void 0?this.applicationSupported=d.applicationSupported:d&&this.applicationSupported!==null&&(d.applicationSupported=this.applicationSupported),this.viewData={...this.viewData,health:s,...!this.viewData.apis&&d?.apis?{apis:d.apis}:{},...!this.viewData.interfaces&&d?.interfaces?{interfaces:d.interfaces}:{}},this.applicationSupported===null&&this.ensureApplicationSupport(e)}):i==="APIs"?this.browse(()=>Bt(this.connection,e),s=>{this.viewData={...this.viewData,apis:s};let o=this.capabilities.get(e);o&&this.viewData.health?.serial===e&&this.viewData.health.firmware_version===o.firmware?o.apis=s:o&&delete o.apis}):this.browse(()=>Vt(this.connection,e),s=>{this.viewData={...this.viewData,interfaces:s};let o=this.capabilities.get(e);o&&this.viewData.health?.serial===e&&this.viewData.health.firmware_version===o.firmware?o.interfaces=s:o&&delete o.interfaces,a&&(this.selectedInterface=null)})}}async showInterface(e,i){if(i==="applications"){let s=this.openApplications(e);return this.updateComplete.then(()=>this.renderRoot.querySelector(".device-views axis-button.active")?.focus()),s}let a=this.selectedInterface===i;if(this.selectedInterface=i,!a&&this.viewData.interfaceResults?.has(i)){this.useCachedView();return}return this.browse(()=>Nt(this.connection,e,i),s=>{let o=new Map(this.viewData.interfaceResults);o.set(i,s),this.viewData={...this.viewData,interfaceResults:o}},"interface")}resetApplicationSupport(){++this.applicationSupportRequest,this.applicationSupportPending=null,this.applicationSupported=null,this.applicationSupportError=""}async ensureApplicationSupport(e){if(this.applicationSupported!==null)return;if(this.applicationSupportPending?.serial===e)return this.applicationSupportPending.promise;let i=++this.applicationSupportRequest;this.applicationSupportError="";let a=jt(this.connection,e).then(({apis:s,supported:o})=>{if(i!==this.applicationSupportRequest||this.selected!==e)return;this.applicationSupported=o;let r=s!==null&&!this.viewData.apis;s&&r&&(this.viewData={...this.viewData,apis:s});let l=this.capabilities.get(e);l&&this.viewData.health?.serial===e&&this.viewData.health.firmware_version===l.firmware&&(l.applicationSupported=o,s&&r&&!l.apis&&(l.apis=s))},s=>{i===this.applicationSupportRequest&&this.selected===e&&(this.applicationSupportError=s.message)}).finally(()=>{i===this.applicationSupportRequest&&(this.applicationSupportPending=null,this.requestUpdate())});return this.applicationSupportPending={serial:e,promise:a},a}async openApplications(e,i=!1){if(this.applicationPending)return;let a=++this.operation;this.loading=null,this.applicationsOpen=!0,this.restartConfirming=!1;let s=this.applicationViews.get(e);this.applications=s?.applications??null,this.applicationUpdates=s?.updates??[],this.applicationPolicy=s?.policy??null,this.applicationsStale=!1,this.selectedApplication=null,this.error="",this.applicationMessage="",this.applicationConfirmation=null,this.installationOpen=!1,this.installationFile=null,this.installationError="",i&&this.applicationSupported!==!0&&this.resetApplicationSupport(),await this.ensureApplicationSupport(e),!(this.operation!==a||!this.applicationsOpen||this.selected!==e)&&this.applicationSupported===!0&&(this.loadApplicationInfo(e),await this.loadApplications(e))}invalidateDeviceViews(e){this.applicationViews.delete(e),this.capabilities.delete(e),this.viewData={}}async loadApplications(e){let i=++this.operation,a=this.applicationPending;this.applicationLoading=!0;try{let s=await Ve(this.connection,e);this.operation===i&&this.applicationsOpen&&(!this.applicationPending||a)&&(this.applications=s,this.applicationViews.set(e,{applications:s,updates:this.applicationUpdates,policy:this.applicationPolicy}),this.applicationsStale=!1,this.selectedApplication&&(this.selectedApplication=s.find(o=>o.name===this.selectedApplication?.name)??null),this.loadAcapUpdates(e))}catch(s){this.operation===i&&this.applicationsOpen&&(!this.applicationPending||a)&&(this.applicationsStale=this.applications!==null,this.applicationFailed=!0,this.selectedApplication=null,this.applicationMessage=this.applicationMessage?`${this.applicationMessage} Refresh failed: ${s.message}`:s.message)}finally{this.operation===i&&(this.applicationLoading=!1)}}clearApplicationUpdates(){++this.updatesRequest,clearTimeout(this.updatesTimer),this.applicationUpdates=[],this.applicationUpdatesError="",this.updateApp=null,this.expandedUpdates=!1,this.updateConfirmation=null,this.updateRecovery=null}async loadAcapUpdates(e){clearTimeout(this.updatesTimer);let i=++this.updatesRequest;try{let a=await this.connection.callWS("acap/catalog",{});if(a.error)throw new Error(a.error);let s=a.folder&&a.packages.length?await Wt(this.connection,e):[];if(i===this.updatesRequest&&this.applicationsOpen&&this.selected===e){let o=s.map(l=>({...l,candidates:[...l.candidates].sort((d,u)=>He(d.package.version,u.package.version))}));this.applicationUpdates=o;let r=this.applicationViews.get(e);r&&(r.updates=o),this.applicationUpdatesError=""}}catch(a){if(i===this.updatesRequest&&this.applicationsOpen){this.applicationUpdates=[];let s=this.applicationViews.get(e);s&&(s.updates=[]),this.applicationUpdatesError=a.message}}finally{i===this.updatesRequest&&this.applicationsOpen&&this.selected===e&&(this.updatesTimer=setTimeout(()=>{this.loadAcapUpdates(e)},6e4))}}async loadArchitecture(e){let i=++this.architectureRequest;this.applicationArchitecture="Loading\u2026";try{let a=await qt(this.connection,e);i===this.architectureRequest&&this.applicationsOpen&&(this.applicationArchitecture=a)}catch(a){i===this.architectureRequest&&this.applicationsOpen&&(this.applicationArchitecture=`Unavailable: ${a.message}`)}}async loadApplicationInfo(e){let i=++this.applicationPolicyRequest;this.applicationPolicy===null&&(this.applicationPolicyError="Loading\u2026");try{let a=await Gt(this.connection,e);if(i===this.applicationPolicyRequest&&this.applicationsOpen&&this.selected===e){this.applicationPolicy=a;let s=this.applicationViews.get(e);s&&(s.policy=a),this.applicationPolicyError=""}}catch(a){if(i===this.applicationPolicyRequest&&this.applicationsOpen&&this.selected===e){this.applicationPolicy=null;let s=this.applicationViews.get(e);s&&(s.policy=null),this.applicationPolicyError=`Unavailable: ${a.message}`}}}async loadApplicationSdks(e){let i=++this.applicationInfoRequest;this.applicationSdks="Loading\u2026";try{let a=await Jt(this.connection,e);i===this.applicationInfoRequest&&this.installationOpen&&(this.applicationSdks=a.length?a.join(", "):"None reported")}catch(a){i===this.applicationInfoRequest&&this.installationOpen&&(this.applicationSdks=`Unavailable: ${a.message}`)}}async applyPolicy(e){let i=this.applicationPolicy;if(!(i===null||this.applicationPending||this.status!=="connected")){++this.applicationPolicyRequest,this.applicationPending=!0;try{await Zt(this.connection,e.serial,i,!i),this.applicationPolicy=!i,this.applicationPolicyError=""}catch(a){this.applicationPolicy=null,this.applicationPolicyError=a.message}finally{this.applicationPending=!1}}}async applyLicense(e){let i=this.licenseSelection;if(!(!i||this.licenseAppName!==i.name||!this.applications?.includes(i)||this.applicationPending||this.status!=="connected")){this.applicationPending=!0,this.applicationMessage="",this.licenseError="";try{await Qt(this.connection,e.serial,i),this.licenseSelection=null,this.licenseOpen=!1,this.licenseAppName="",this.licenseFile=null,this.applicationFailed=!1,this.applicationMessage="License change accepted.",this.invalidateDeviceViews(e.serial),await this.loadApplications(e.serial)}catch(a){this.licenseSelection=null,this.licenseAppName="",this.licenseFile=null,this.licenseError=a.message,this.applicationFailed=!0,this.applicationMessage=a.message,this.applications=null,this.invalidateDeviceViews(e.serial)}finally{this.applicationPending=!1,this.licenseOpen||this.updateComplete.then(()=>this.renderRoot.querySelector(".license-trigger")?.focus())}}}closeLicense(e){e?.preventDefault(),e?.stopPropagation(),!this.applicationPending&&(this.licenseOpen=!1,this.licenseSelection=null,this.licenseAppName="",this.licenseFile=null,this.licenseError="",this.licenseDragging=!1,this.updateComplete.then(()=>this.renderRoot.querySelector(".license-trigger")?.focus()))}selectLicenseFile(e){if(!e||e.length===0||this.applicationPending)return;if(this.licenseFile=null,this.licenseError="",e.length!==1){this.licenseError="Choose one license file.";return}let i=e[0];if(!i.size||i.size>1024*1024){this.licenseError="Choose a non-empty license file up to 1 MiB.";return}this.licenseFile=i}async uploadLicense(e){let i=this.licenseFile,a=this.applications?.find(s=>s.name===this.licenseAppName);if(!(!i||!a||this.licenseSelection||this.applicationPending||this.status!=="connected")){this.applicationPending=!0,this.applicationMessage="",this.licenseError="";try{await ei(this.connection,e.serial,a,i),this.licenseOpen=!1,this.licenseFile=null,this.licenseAppName="",this.applicationFailed=!1,this.applicationMessage="License change accepted.",this.invalidateDeviceViews(e.serial),await this.loadApplications(e.serial)}catch(s){this.licenseFile=null,this.licenseAppName="",this.licenseError=s.message,this.applicationFailed=!0,this.applicationMessage=s.message,this.applications=null,this.invalidateDeviceViews(e.serial)}finally{this.applicationPending=!1,this.licenseOpen||this.updateComplete.then(()=>this.renderRoot.querySelector(".license-trigger")?.focus())}}}closeApplications(e=!0){this.applicationPending||(++this.operation,this.applicationsOpen=!1,this.clearApplicationUpdates(),++this.architectureRequest,++this.applicationInfoRequest,++this.applicationPolicyRequest,this.applicationArchitecture="",this.applicationSdks="",this.applicationPolicy=null,this.licenseSelection=null,this.licenseOpen=!1,this.licenseAppName="",this.licenseFile=null,this.licenseError="",this.licenseDragging=!1,this.applicationLoading=!1,this.selectedApplication=null,this.applicationConfirmation=null,this.installationOpen=!1,this.installationFile=null,this.installationError="",this.installationDragging=!1,this.applicationMessage="",e&&(this.updateComplete.then(()=>(this.renderRoot.querySelector(".application-trigger")??this.renderRoot.querySelector(".device-views axis-button.active"))?.focus()),this.selected&&this.status==="connected"&&this.showDeviceView(this.selected,this.deviceView)))}async applyApplicationAction(e){let i=this.applicationConfirmation;if(!(!i||this.applicationPending)){this.applicationPending=!0,this.applicationMessage="";try{await ii(this.connection,e.serial,i.app,i.action),this.applicationConfirmation=null,this.applicationFailed=!1,this.applicationMessage="Application action accepted.",this.invalidateDeviceViews(e.serial),await this.loadApplications(e.serial)}catch(a){this.applicationConfirmation=null,this.selectedApplication=null,this.applicationFailed=!0,this.applicationMessage=a.message,this.applications=null,this.invalidateDeviceViews(e.serial)}finally{this.applicationPending=!1}}}async applyApplicationUpdate(e){let i=this.updateConfirmation;if(!(!i||!this.applications?.includes(i.app)||this.applicationPending||this.status!=="connected")){this.applicationPending=!0,this.applicationMessage="";try{await Kt(this.connection,e.serial,i.app,i.candidate),this.updateConfirmation=null,this.updateApp=null,this.applicationFailed=!1,this.applicationMessage="Application updated.",this.invalidateDeviceViews(e.serial),await this.loadApplications(e.serial)}catch(a){this.updateConfirmation=null,this.applicationsStale=!0,this.updateRecovery={...i,message:a.message,eligible:a instanceof ne&&a.deviceCode===27,status:this.status==="connected"?"checking":"unavailable",confirming:!1,refreshError:""},this.invalidateDeviceViews(e.serial)}finally{this.applicationPending=!1}this.updateRecovery&&await this.refreshUpdateRecovery(e.serial)}}async refreshUpdateRecovery(e){if(!this.updateRecovery||this.status!=="connected")return;this.applicationsStale=!0;let i=this.updateRecovery={...this.updateRecovery,status:"checking",confirming:!1,refreshError:""},a=++this.operation;this.applicationLoading=!0;try{let s=await Ve(this.connection,e);if(this.operation!==a||this.updateRecovery!==i)return;let o=s.find(r=>r.name===i.app.name);this.applications=s,this.applicationsStale=!1,this.updateRecovery={...i,status:o?o.version===i.app.version&&o.status===i.app.status&&o.vendor===i.app.vendor?"installed":"changed":"missing"}}catch(s){this.operation===a&&this.updateRecovery===i&&(this.updateRecovery={...i,status:"unavailable",refreshError:s.message})}finally{this.operation===a&&(this.applicationLoading=!1)}}async applyApplicationReplacement(e){let i=this.updateRecovery;if(!(!i||!i.confirming||!i.eligible||!i.candidate.replacement||!["installed","missing"].includes(i.status)||this.applicationPending||this.status!=="connected"||this.applicationsStale)){this.applicationPending=!0;try{await this.connection.replaceApplication(e.serial,i.app,i.candidate,i.status==="installed"),this.updateRecovery=null,this.updateApp=null,this.applicationFailed=!1,this.applicationMessage="Application installed.",this.invalidateDeviceViews(e.serial),await this.loadApplications(e.serial)}catch(a){this.updateRecovery={...i,message:a.message,status:this.status==="connected"?"checking":"unavailable",confirming:!1,refreshError:""},this.applicationsStale=!0,this.invalidateDeviceViews(e.serial)}finally{this.applicationPending=!1}this.updateRecovery&&await this.refreshUpdateRecovery(e.serial)}}closeUpdateDialog(e){if(e?.preventDefault(),e?.stopPropagation(),!this.applicationPending){if(e?.type==="cancel"&&this.updateConfirmation){this.backToUpdateVersions();return}this.updateRecovery&&!this.applicationsStale&&!this.applications?.some(i=>i.name===this.updateRecovery?.app.name)?this.selectedApplication=null:this.updateRecovery&&!this.applicationsStale&&(this.selectedApplication=this.applications?.find(i=>i.name===this.updateRecovery?.app.name)??null),this.updateRecovery=null,this.updateApp=null,this.updateConfirmation=null,this.expandedUpdates=!1}}backToUpdateVersions(){let e=this.updateConfirmation?.candidate.package.filename;this.updateConfirmation=null,this.updateComplete.then(()=>Array.from(this.renderRoot.querySelectorAll(".update-dialog axis-button[data-package-file]")).find(i=>i.getAttribute("data-package-file")===e)?.focus())}async loadInstallCandidates(e){this.installDetail=null;let i=++this.installCandidatesRequest;this.installCandidatesLoading=!0,this.installCandidates=null,this.installCandidatesError="",this.installCandidate=null;try{let a=await this.connection.callWS("acap/catalog",{});if(a.error)throw new Error(a.error);let s=a.folder&&a.packages.length?await Xt(this.connection,e):[];i===this.installCandidatesRequest&&this.installationOpen&&this.selected===e&&(this.installCandidates=[...s].sort((o,r)=>He(o.package.version,r.package.version)),a.errors.length&&(this.installCandidatesError="Some packages could not be inspected. Check Server settings."))}catch(a){i===this.installCandidatesRequest&&this.installationOpen&&(this.installCandidatesError=a.message)}finally{i===this.installCandidatesRequest&&(this.installCandidatesLoading=!1)}}openInstallation(e){this.applicationMessage="",this.installationError="",this.installationOpen=!0,this.installAppsExpanded=!1,this.installExpandedApp="",this.installCandidatesExpanded=!1,this.loadArchitecture(e),this.loadApplicationSdks(e),this.loadInstallCandidates(e)}closeInstallation(e){e?.preventDefault(),e?.stopPropagation(),!this.applicationPending&&(this.installDetail=null,++this.architectureRequest,++this.applicationInfoRequest,this.installationOpen=!1,this.installationFile=null,++this.installCandidatesRequest,this.installCandidates=null,this.installCandidatesLoading=!1,this.installCandidatesError="",this.installCandidate=null,this.installationError="",this.installationDragging=!1,this.updateComplete.then(()=>this.renderRoot.querySelector(".installation-trigger")?.focus()))}selectInstallationFile(e){if(!e||e.length===0||this.applicationPending)return;if(this.installationFile=null,this.installCandidate=null,this.installationError="",e.length!==1){this.installationError="Choose one application package.";return}let i=e[0];if(!i.name.toLowerCase().endsWith(".eap")||i.size===0||i.size>1024*1024*1024){this.installationError="Choose a non-empty .eap file up to 1024 MB (1 GiB).";return}this.installationFile=i}async applyInstallation(e){let i=this.installationFile,a=this.installCandidate;if(!(!i&&!a||this.applicationPending||this.status!=="connected")){this.applicationPending=!0,this.applicationMessage="",this.installationError="";try{a?await Yt(this.connection,e.serial,a):i&&await ti(this.connection,e.serial,i),this.installationOpen=!1,this.installationFile=null,this.installCandidate=null,++this.installCandidatesRequest,this.applicationFailed=!1,this.applicationMessage="Application installed.",this.invalidateDeviceViews(e.serial),await this.loadApplications(e.serial)}catch(s){this.installationFile=null,this.installCandidate=null,this.applicationFailed=!0,this.applicationMessage=s.message,this.installationError=s.message,this.applications=null,this.invalidateDeviceViews(e.serial)}finally{this.applicationPending=!1,this.installationOpen||this.updateComplete.then(()=>this.renderRoot.querySelector(".installation-trigger")?.focus())}}}applicationUrl(e,i){let a=i.configuration_page;if(!a||a.includes("\\")||!/^\/?local\//.test(a))return null;try{let s=e.port?`:${e.port}`:"",o=new URL(`${e.web_proto}://${e.host}${s}`);if(o.protocol!=="http:"&&o.protocol!=="https:"||o.username||o.password)return null;let r=new URL(a.startsWith("/")?a:`/${a}`,o);return r.origin===o.origin&&r.pathname.startsWith("/local/")?r.href:null}catch{return null}}renderApplications(e,i){if(this.applicationSupported!==!0)return c`<axis-card>
        <h3>Installed applications</h3>
        ${this.applicationSupportError?c`<p role="alert">${this.applicationSupportError}</p>`:this.applicationSupported===!1?c`<p>Applications are not supported by this device.</p>`:c`<p role="status">Checking application support…</p>`}
        ${this.applicationSupportError||this.applicationSupported===!1?c`<axis-button
                ?disabled=${!i||this.applicationSupportPending!==null}
                @click=${()=>this.openApplications(e.serial,!0)}
                >Retry support check</axis-button
              >`:p}
      </axis-card>`;let a=!i||this.applicationsStale||this.applicationLoading&&this.applications===null||this.applicationPending||this.applicationConfirmation!==null||this.updateApp!==null||this.updateConfirmation!==null||this.licenseSelection!==null||this.installationOpen||this.licenseOpen||this.applicationSupported!==!0;return c`
      <axis-card>
        <div class="application-heading">
          <h3>Installed applications</h3>
          <div class="actions">
            <axis-button
              class="installation-trigger"
              variant="brand"
              ?disabled=${a}
              @click=${()=>this.openInstallation(e.serial)}
              >Install application</axis-button
            >
            <axis-button
              class="license-trigger"
              ?disabled=${a||!this.applications?.length}
              @click=${()=>{this.applicationMessage="",this.licenseError="",this.licenseOpen=!0}}
              >Manage licenses</axis-button
            >
          </div>
        </div>
        <div>
          <label class="policy-toggle">
            <input
              type="checkbox"
              role="switch"
              .checked=${this.applicationPolicy===!0}
              ?disabled=${a||this.applicationPolicy===null}
              @change=${s=>{let o=s.currentTarget;o.checked=this.applicationPolicy===!0,this.applyPolicy(e)}}
            />
            Allow unsigned applications (AllowUnsigned)
          </label>
          ${this.applicationPolicy===null?c`<p role="status">Policy: ${this.applicationPolicyError}</p>
                  <axis-button
                    ?disabled=${!i||this.applicationPending||this.installationOpen||this.licenseOpen}
                    @click=${()=>this.loadApplicationInfo(e.serial)}
                    >Refresh application information</axis-button
                  >`:p}
        </div>
        ${this.applicationMessage?c`<p role=${this.applicationFailed?"alert":"status"}>
                ${this.applicationMessage}
              </p>`:p}
        ${this.applicationsStale?c`<p role="status">Application list may be out of date.</p>
                <axis-button
                  ?disabled=${!i||this.applicationLoading||this.applicationPending||this.updateApp!==null}
                  @click=${()=>this.loadApplications(e.serial)}
                  >Refresh applications</axis-button
                >`:p}
        ${this.applications?.length===0?c`<p>No applications installed.</p>`:p}
        ${this.applicationUpdatesError?c`<p role="alert">Update check failed: ${this.applicationUpdatesError}</p>`:p}
        <ul class="application-list" aria-label="Applications">
          ${this.applications?.slice().sort((s,o)=>(s.nice_name||s.name).localeCompare(o.nice_name||o.name,void 0,{numeric:!0})).map(s=>{let r=this.applicationUpdates.find(d=>d.name===s.name&&d.version===s.version&&d.status===s.status)?.candidates.find(d=>!d.downgrade&&d.warnings.length===0),l=r?.findings.some(d=>d.kind==="not_checked");return c`
                <li>
                  <axis-button
                    ?disabled=${a}
                    @click=${()=>{this.applicationMessage="",this.selectedApplication=s}}
                  >
                    <span class="application-info">
                      <span>${s.nice_name||s.name}</span>
                      <span class="application-meta">
                        ${s.status||"Unknown"} — Version
                        ${s.version||"Unknown"} — Signature:
                        ${s.signature_status||"Unknown"}
                      </span>
                      ${r?c`<span class="application-meta ${l?"update-warning":"application-update"}">${l?"Update candidate":"Update available"}: ${r.package.version}${l?" \u2014 verification incomplete":""}</span>`:p}
                    </span>
                  </axis-button>
                </li>
              `})}
        </ul>
      </axis-card>
    `}closeApplicationDialog(e){e?.preventDefault(),e?.stopPropagation(),!this.applicationPending&&(this.selectedApplication=null,this.applicationConfirmation=null)}renderApplicationDialog(e,i){let a=this.selectedApplication,s=this.applicationConfirmation,o=this.applicationUpdates.find(u=>u.name===a?.name&&u.version===a.version&&u.status===a.status),r=!i||this.applicationsStale||this.applicationSupported!==!0||this.applicationLoading&&this.applications===null||this.applicationPending||this.updateApp!==null,l=a?this.applicationUrl(e,a):null,d=a?.status==="Running"&&!r;return c`
      <dialog
        class="application-dialog"
        aria-labelledby="application-dialog-title"
        @cancel=${this.closeApplicationDialog}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="application-dialog-title">
              ${a?.nice_name||a?.name||""}
            </h2>
            <div class="dialog-controls">
              <button
                type="button"
                ?disabled=${this.applicationPending}
                @click=${this.closeApplicationDialog}
              >
                Close
              </button>
            </div>
          </header>
        </div>
        <div class="dialog-content">
          ${a?c`
                  <span class="application-status" data-status=${a.status}
                    >${a.status}</span
                  >
                  ${this.applicationMessage?c`<p role=${this.applicationFailed?"alert":"status"}>${this.applicationMessage}</p>`:p}
                  ${this.applicationsStale?c`<p role="status">
                            Application details may be out of date.
                          </p>
                          <axis-button
                            ?disabled=${!i||this.applicationLoading||this.applicationPending||this.updateApp!==null}
                            @click=${()=>this.loadApplications(e.serial)}
                            >Refresh applications</axis-button
                          >`:p}
                  ${this.applicationSupportError?c`<p role="alert">${this.applicationSupportError} Close this dialog to retry the support check.</p>`:this.applicationSupported===!1?c`<p role="alert">Applications are not supported by this device. Close this dialog to retry the support check.</p>`:p}
                  <dl>
                    <dt>Package</dt>
                    <dd>${a.name}</dd>
                    <dt>Version</dt>
                    <dd>${a.version||"Unknown"}</dd>
                    <dt>Vendor</dt>
                    <dd>${a.vendor||"Unknown"}</dd>
                    <dt>License</dt>
                    <dd>${a.license_status}</dd>
                    ${a.bundled?c`<dt>Bundled</dt>
                            <dd>${a.bundled}</dd>`:p}
                    ${a.signature_status?c`<dt>Signature</dt>
                            <dd>${a.signature_status}</dd>`:p}
                    ${a.resources?.length?c`<dt>Resources</dt>
                            <dd>
                              ${a.resources.map(u=>`${u.name||"Unknown"}: ${u.used||"Unknown"}`).join(", ")}
                            </dd>`:p}
                    ${a.compatible_os_versions?.length?c`<dt>Compatible OS versions</dt>
                            <dd>
                              ${a.compatible_os_versions.map(u=>`${u.Min||"Any"} \u2013 ${u.Max||"Any"}`).join(", ")}
                            </dd>`:p}
                    ${a.application_id?c`<dt>Application ID</dt>
                            <dd>${a.application_id}</dd>`:p}
                    ${a.license_expiration_date?c`<dt>License expires</dt>
                            <dd>${a.license_expiration_date}</dd>`:p}
                  </dl>
                  ${o?c`<axis-button
                          ?disabled=${r}
                          @click=${()=>{this.applicationMessage="",this.updateApp=a,this.expandedUpdates=!1}}
                          >View versions
                          (${o.candidates.length})</axis-button
                        >`:p}
                  ${s?.app===a?c` <p>
                            ${s.action==="remove"?`Uninstall ${a.nice_name||a.name} and remove its data?`:`${s.action==="start"?"Start":s.action==="restart"?"Restart":"Stop"} ${a.nice_name||a.name}?`}
                          </p>
                          <div class="actions">
                            <axis-button
                              variant=${s.action==="remove"?"danger":"brand"}
                              .busy=${this.applicationPending}
                              ?disabled=${r}
                              @click=${()=>this.applyApplicationAction(e)}
                              >Confirm
                              ${s.action==="remove"?"uninstall":s.action}</axis-button
                            >
                            <axis-button
                              ?disabled=${this.applicationPending}
                              @click=${()=>this.applicationConfirmation=null}
                              >Cancel</axis-button
                            >
                          </div>`:c` <div class="actions">
                          ${a.status==="Running"||a.status==="Stopped"?c`<axis-button
                                  ?disabled=${r}
                                  @click=${()=>{this.applicationMessage="",this.applicationConfirmation={app:a,action:a.status==="Running"?"stop":"start"}}}
                                  >${a.status==="Running"?"Stop":"Start"}</axis-button
                                >`:p}
                          ${a.status==="Running"?c`<axis-button
                                  ?disabled=${r}
                                  @click=${()=>{this.applicationMessage="",this.applicationConfirmation={app:a,action:"restart"}}}
                                  >Restart</axis-button
                                >`:p}
                          ${l?c`<axis-button
                                  href=${d?l:p}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  ?disabled=${!d}
                                  >Open configuration</axis-button
                                >`:a.configuration_page?c`<span
                                    >Configuration link unavailable</span
                                  >`:p}
                          <axis-button
                            variant="danger"
                            ?disabled=${r}
                            @click=${()=>{this.applicationMessage="",this.applicationConfirmation={app:a,action:"remove"}}}
                            >Uninstall</axis-button
                          >
                        </div>`}
                `:p}
        </div>
      </dialog>
    `}renderAcapFindings(e){let i={incompatible:"Incompatible",unknown:"Unknown",not_checked:"Not checked",review:"Review"};return e.findings.map(a=>c`<p class=${a.kind==="not_checked"?"":"update-warning"}>
          ${i[a.kind]}: ${a.message}
        </p>`)}renderAcapCandidates(e,i,a,s,o,r,l){return c`
      <ul class="application-list" aria-label="Package versions">
        ${(i?e:e.slice(0,5)).map(d=>c`<li>
              <axis-button
                data-package-file=${d.package.filename}
                ?disabled=${a}
                .pressed=${s==="install"?d===l:void 0}
                @click=${()=>o(d)}
              >
                <span class="application-info">
                  <span>Version ${d.package.version||"Unknown"}</span>
                  <span class="application-meta"
                    >${d.package.vendor||"Unknown vendor"} —
                    Signature:
                    ${d.package.signature==="present_unverified"?"present, not verified":d.package.signature==="not_detected"?"not detected":"unknown"}</span
                  >
                  ${d===l?c`<span class="application-meta">Selected</span>`:p}
                  ${this.renderCandidateBadges(d,d===e[0])}
                </span>
              </axis-button>
            </li>`)}
      </ul>
      ${e.length>5?c`<axis-button ?disabled=${a} .expanded=${i} @click=${r}>${i?"Show fewer versions":`Show ${e.length-5} more ${e.length===6?"version":"versions"}`}</axis-button>`:p}
    `}closeInstallDetail(e){e?.preventDefault(),e?.stopPropagation(),this.installDetail=null}renderCandidateBadges(e,i=!1){let a=e.findings.some(o=>o.kind==="incompatible"),s=e.findings.some(o=>o.kind==="unknown");return c`
      ${i&&ai(e.package.version)?c`<span class="application-meta">Newest</span>`:p}
      ${e.downgrade?c`<span class="application-meta update-warning">Downgrade</span>`:p}
      ${a?c`<span class="application-meta update-warning">Declared incompatibility</span>`:p}
      ${s?c`<span class="application-meta update-warning">Verification incomplete</span>`:p}
      ${e.warnings.length&&!a&&!s&&!e.downgrade?c`<span class="application-meta update-warning">Review needed</span>`:p}
    `}renderPackageDetails(e){let i=e.package;return c`
      <dl>
        <dt>Application</dt>
        <dd>${i.friendly_name||i.name||"Unknown"}</dd>
        <dt>Version</dt>
        <dd>${i.version||"Unknown"}</dd>
        <dt>Source</dt>
        <dd>Server catalog</dd>
        <dt>Vendor</dt>
        <dd>${i.vendor||"Unknown"}</dd>
        <dt>Signature</dt>
        <dd>
          ${i.signature==="present_unverified"?"Present, not verified":i.signature==="not_detected"?"Not detected":"Unknown"}
        </dd>
        <dt>Compatible AXIS OS</dt>
        <dd>
          ${i.os_ranges?.length?i.os_ranges.map(([a,s])=>`${a||"?"}\u2013${s||"?"}`).join(", "):"Unknown"}
        </dd>
      </dl>
      ${this.renderAcapFindings(e)}
      <details>
        <summary>Technical details</summary>
        <dl>
          <dt>File</dt>
          <dd>${i.filename}</dd>
          <dt>Vendor ID</dt>
          <dd>${i.vendor_id||"Unknown"}</dd>
          <dt>Architecture</dt>
          <dd>${i.architecture||"Unknown"}</dd>
          <dt>SDK</dt>
          <dd>${i.sdk||"Unknown"}</dd>
          <dt>Size</dt>
          <dd>
            ${i.size===void 0?"Unknown":`${i.size} bytes`}
          </dd>
        </dl>
      </details>
    `}renderInstallDetail(e){let i=this.installDetail,a=i?.package;return c`<dialog
      class="package-dialog"
      aria-labelledby="package-dialog-title"
      @cancel=${this.closeInstallDetail}
    >
      <div class="dialog-header">
        <header class="dialog-heading">
          <h2 id="package-dialog-title">
            ${a?.friendly_name||a?.name||"Package"} —
            ${a?.version||"Unknown version"}
          </h2>
          <div class="dialog-controls">
            <button type="button" @click=${this.closeInstallDetail}>
              Close
            </button>
          </div>
        </header>
      </div>
      <div class="dialog-content">
        ${i&&a?c`
                ${this.renderPackageDetails(i)}
                <axis-button
                  variant="brand"
                  ?disabled=${!e||this.applicationPending||!this.installCandidates?.includes(i)}
                  @click=${()=>{this.installCandidate=i,this.installationFile=null,this.installationError="",this.installDetail=null,this.updateComplete.then(()=>this.renderRoot.querySelector(".installation-selection")?.focus())}}
                  >Select package</axis-button
                >
              `:p}
      </div>
    </dialog>`}renderUpdateDialog(e,i){let a=this.updateApp,s=this.updateConfirmation,o=this.updateRecovery,r=this.applicationUpdates.find(l=>l.name===a?.name&&l.version===a.version&&l.status===a.status);return c`
      <dialog
        class="update-dialog"
        aria-labelledby="update-dialog-title"
        @cancel=${this.closeUpdateDialog}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="update-dialog-title">
              Application versions: ${a?.nice_name||a?.name||""}
            </h2>
            <div class="dialog-controls">
              <button
                type="button"
                ?disabled=${this.applicationPending}
                @click=${this.closeUpdateDialog}
              >
                Close
              </button>
            </div>
          </header>
        </div>
        <div class="dialog-content">
          ${o?c`
                  <p role="alert">${o.message}</p>
                  <p>
                    Package: ${o.candidate.package.filename}
                    (${o.candidate.package.version||"unknown version"})
                  </p>
                  ${o.status==="checking"?c`<p role="status">
                          Checking installed applications…
                        </p>`:o.status==="unavailable"?c`<p role="alert">
                              Could not check installed
                              applications${o.refreshError?`: ${o.refreshError}`:"."}
                            </p>
                            <axis-button
                              ?disabled=${!i||this.applicationPending}
                              @click=${()=>this.refreshUpdateRecovery(e.serial)}
                              >Check applications</axis-button
                            >`:o.status==="changed"?c`<p role="alert">
                              The application changed. Close this dialog and
                              review its current state before continuing.
                            </p>`:o.status==="missing"?c`<p>
                                The application is no longer installed.
                              </p>`:c`<p>The application is still installed.</p>`}
                  ${o.eligible&&o.candidate.replacement&&(o.status==="installed"||o.status==="missing")?o.confirming?c` <p>
                              ${o.status==="installed"?`Remove ${o.app.nice_name||o.app.name} ${o.app.version||"unknown version"} and install ${o.candidate.package.version||"unknown version"}? Removal deletes the application's data and settings. The new installation may fail.`:`Install ${o.candidate.package.version||"unknown version"}? The device will make the final compatibility and signature checks.`}
                            </p>
                            ${this.renderAcapFindings({...o.candidate,...o.candidate.replacement})}
                            <div class="actions">
                              <axis-button
                                variant=${o.status==="installed"?"danger":"brand"}
                                .busy=${this.applicationPending}
                                ?disabled=${!i||this.applicationPending}
                                @click=${()=>this.applyApplicationReplacement(e)}
                                >Confirm
                                ${o.status==="installed"?"remove and install":"install"}</axis-button
                              >
                              <axis-button
                                ?disabled=${this.applicationPending}
                                @click=${()=>this.updateRecovery={...o,confirming:!1}}
                                >Cancel</axis-button
                              >
                            </div>`:c` <p>
                              ${o.status==="installed"?"The device rejected this upgrade because the vendor IDs differ. Removing the existing application allows you to try installing this package instead.":"You can install the reviewed package now that the application is absent."}
                            </p>
                            <axis-button
                              variant=${o.status==="installed"?"danger":"brand"}
                              ?disabled=${!i||this.applicationPending}
                              @click=${()=>this.updateRecovery={...o,confirming:!0}}
                              >${o.status==="installed"?"Remove and install":"Install"}</axis-button
                            >`:p}
                `:s&&a?c`
                    ${this.renderPackageDetails(s.candidate)}
                    <p>
                      Change ${a.nice_name||a.name} from
                      ${a.version||"unknown version"} to
                      ${s.candidate.package.version||"unknown version"}
                      using ${s.candidate.package.filename}? An
                      interrupted or failed upgrade can remove both versions.
                      Signature status:
                      ${s.candidate.package.signature==="present_unverified"?"present, not verified":s.candidate.package.signature==="not_detected"?"not detected":"unknown"}.
                      The device makes the final vendor ID and signature checks.
                    </p>
                    ${s.candidate.warnings.length?c`<p>Confirming acknowledges these findings; the device may still reject the package.</p>`:p}
                    <div class="actions">
                      <axis-button
                        variant="brand"
                        .busy=${this.applicationPending}
                        ?disabled=${!i||this.applicationPending}
                        @click=${()=>this.applyApplicationUpdate(e)}
                        >Confirm
                        ${s.candidate.downgrade?"downgrade":"update"}</axis-button
                      >
                      <axis-button
                        ?disabled=${this.applicationPending}
                        @click=${()=>this.backToUpdateVersions()}
                        >Back to versions</axis-button
                      >
                    </div>
                  `:r&&a?this.renderAcapCandidates(r.candidates,this.expandedUpdates,!i||this.applicationPending,"update",l=>this.updateConfirmation={app:a,candidate:l},()=>this.expandedUpdates=!this.expandedUpdates):c`<p>
                      Versions are no longer available. Close and refresh the
                      application list.
                    </p>`}
        </div>
      </dialog>
    `}renderInstallationDialog(e,i){let a=new Map;for(let o of this.installCandidates??[]){let r=o.package.name,l=a.get(r);l?l.push(o):a.set(r,[o])}let s=[...a.entries()].sort(([,o],[,r])=>(o[0].package.friendly_name||o[0].package.name).localeCompare(r[0].package.friendly_name||r[0].package.name,void 0,{numeric:!0}));return c`
      <dialog
        class="installation-dialog"
        aria-labelledby="installation-dialog-title"
        @cancel=${this.closeInstallation}
        @dragover=${o=>o.preventDefault()}
        @drop=${o=>o.preventDefault()}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="installation-dialog-title">Install application</h2>
            <div class="dialog-controls">
              <button
                type="button"
                ?disabled=${this.applicationPending}
                @click=${this.closeInstallation}
              >
                Close
              </button>
            </div>
          </header>
        </div>
        <div class="dialog-content">
          <p>
            Choose a server package or upload an .eap file up to 1024 MB (1
            GiB). Administrator credentials are required.
          </p>
          <details>
            <summary>Device requirements</summary>
            <p>Hardware architecture: ${this.applicationArchitecture}</p>
            <p>Supported SDKs: ${this.applicationSdks}</p>
            <p>
              Unsigned applications:
              ${this.applicationPolicy===null?this.applicationPolicyError:this.applicationPolicy?"Allowed":"Not allowed"}
            </p>
            <p>
              Signed packages may temporarily require approximately twice their
              size in available device RAM during installation.
            </p>
          </details>
          <h3>Available server packages</h3>
          ${this.installCandidatesLoading?c`<p role="status">Checking server packages…</p>`:p}
          ${this.installCandidatesError?c`<p class="error" role="alert">${this.installCandidatesError}</p>`:p}
          ${this.installCandidates?.length===0?c`<p>No new applications found in the server catalog.</p>`:p}
          <ul class="application-list" aria-label="Suggested applications">
            ${(this.installAppsExpanded?s:s.slice(0,5)).map(([o,r])=>{let l=r[0],d=l.package.friendly_name||o,u=d===o?o:`${d} (${o})`;return c`
                  <li>
                    <axis-button
                      ?disabled=${!i||this.applicationPending}
                      .expanded=${this.installExpandedApp===o}
                      variant=${this.installExpandedApp===o?"brand":"neutral"}
                      @click=${()=>{this.installExpandedApp=this.installExpandedApp===o?"":o,this.installCandidatesExpanded=!1}}
                    >
                      <span class="application-info">
                        <span>${u}</span>
                        <span class="application-meta">
                          ${l.package.vendor||"Unknown vendor"} —
                          Version ${l.package.version||"Unknown"} —
                          Signature:
                          ${l.package.signature==="present_unverified"?"present, not verified":l.package.signature==="not_detected"?"not detected":"unknown"}
                        </span>
                        <span class="application-meta">
                          ${r.length}
                          ${r.length===1?"version":"versions"}
                          available
                        </span>
                        ${this.renderCandidateBadges(l)}
                      </span>
                    </axis-button>
                    ${this.installExpandedApp===o?c`<section
                            class="install-versions"
                            aria-label=${`Versions of ${u}`}
                          >
                            <p>Choose a version of ${d}</p>
                            ${this.renderAcapCandidates(r,this.installCandidatesExpanded,!i||this.applicationPending,"install",g=>{this.installDetail=g},()=>this.installCandidatesExpanded=!this.installCandidatesExpanded,this.installCandidate)}
                          </section>`:p}
                  </li>
                `})}
          </ul>
          ${s.length>5?c`
                  <div class="actions">
                    <axis-button
                      ?disabled=${!i||this.applicationPending}
                      @click=${()=>this.installAppsExpanded=!this.installAppsExpanded}
                      >${this.installAppsExpanded?"Show fewer applications":`Show ${s.length-5} more ${s.length===6?"application":"applications"}`}</axis-button
                    >
                  </div>
                `:p}
          <h3>Choose a package file</h3>
          <div
            class="installation-drop"
            role="region"
            aria-label="Application package drop area"
            ?data-dragging=${this.installationDragging}
            @dragover=${o=>{o.preventDefault(),!(!i||this.applicationPending)&&o.dataTransfer?.types.includes("Files")&&(o.dataTransfer.dropEffect="copy",this.installationDragging=!0)}}
            @dragleave=${o=>{(!(o.relatedTarget instanceof Node)||!o.currentTarget.contains(o.relatedTarget))&&(this.installationDragging=!1)}}
            @drop=${o=>{if(o.preventDefault(),this.installationDragging=!1,!(!i||this.applicationPending)){if(!o.dataTransfer?.files.length){this.installationFile=null,this.installCandidate=null,this.installationError="Drop one application package.";return}this.selectInstallationFile(o.dataTransfer.files)}}}
          >
            <p>Drag and drop an application package here</p>
            <span>or</span>
            <axis-button
              class="choose-file"
              ?disabled=${!i||this.applicationPending}
              .expanded=${this.installAppsExpanded}
              @click=${()=>this.renderRoot.querySelector(".installation-file")?.click()}
              >Choose file</axis-button
            >
            <input
              class="installation-file"
              type="file"
              accept=".eap"
              hidden
              ?disabled=${!i||this.applicationPending}
              @change=${o=>{let r=o.target;this.selectInstallationFile(r.files),r.value=""}}
            />
          </div>
          <section
            class="installation-selection"
            aria-label="Selected application"
            tabindex="-1"
          >
            <h3>Selected application</h3>
            ${this.installCandidate||this.installationFile?c`
                    <p>New applications are not started automatically.</p>
                    ${this.installationFile?c`<p>A matching application may be upgraded or downgraded. If an upgrade fails or is interrupted, both versions may be removed. A running application restarts after an upgrade.</p>`:p}
                  `:p}
            <p role="status">
              ${this.installCandidate?c`<strong>Selected server package:</strong>
                      ${this.installCandidate.package.friendly_name||this.installCandidate.package.name},
                      ${this.installCandidate.package.version||"unknown version"}
                      (${this.installCandidate.package.filename})`:this.installationFile?c`<strong>Selected:</strong>
                        ${this.installationFile.name}`:"No application package selected."}
            </p>
            ${this.installCandidate||this.installationFile?c`
                    <p>
                      Source:
                      ${this.installCandidate?"Server catalog":"Uploaded file"}
                    </p>
                    ${this.installationFile?c`<p>Package metadata and compatibility have not been checked locally. The device validates the uploaded package.</p>`:p}
                    <axis-button
                      ?disabled=${!i||this.applicationPending}
                      @click=${()=>{let o=this.installCandidate?.package.filename;this.installCandidate=null,this.installationFile=null,this.installationError="",this.updateComplete.then(()=>{(Array.from(this.renderRoot.querySelectorAll(".installation-dialog axis-button[data-package-file]")).find(l=>l.getAttribute("data-package-file")===o)??this.renderRoot.querySelector(".installation-dialog .choose-file"))?.focus()})}}
                      >Change selection</axis-button
                    >
                  `:p}
            ${this.installCandidate?c`
                    <p>
                      Signature:
                      ${this.installCandidate.package.signature==="present_unverified"?"present, not verified":this.installCandidate.package.signature==="not_detected"?"not detected":"unknown"}.
                      The device makes the final vendor ID and signature checks.
                    </p>
                    ${this.renderAcapFindings(this.installCandidate)}
                    ${this.installCandidate.warnings.length?c`<p>Confirming acknowledges these findings; the device may still reject the package.</p>`:p}
                  `:p}
          </section>
          ${this.installationError?c`<p class="error" role="alert">
                  ${this.installationError}
                </p>`:p}
          ${this.applicationPending?c`<p role="status">Uploading and installing application…</p>`:p}
          <div class="actions">
            <axis-button
              variant="brand"
              .busy=${this.applicationPending}
              ?disabled=${!i||this.applicationPending||this.installationFile===null&&this.installCandidate===null}
              @click=${()=>this.applyInstallation(e)}
              >Confirm installation</axis-button
            >
            <axis-button
              ?disabled=${this.applicationPending}
              @click=${this.closeInstallation}
              >Cancel</axis-button
            >
          </div>
        </div>
      </dialog>
    `}renderLicenseDialog(e,i){let a=this.applications?.find(s=>s.name===this.licenseAppName);return c`
      <dialog
        class="license-dialog"
        aria-labelledby="license-dialog-title"
        @cancel=${this.closeLicense}
        @dragover=${s=>s.preventDefault()}
        @drop=${s=>s.preventDefault()}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="license-dialog-title">Manage licenses</h2>
            <div class="dialog-controls">
              <button
                type="button"
                ?disabled=${this.applicationPending}
                @click=${this.closeLicense}
              >
                Close
              </button>
            </div>
          </header>
        </div>
        <div class="dialog-content">
          <p>
            Choose an application and a license file up to 1 MiB. Administrator
            credentials are required. Uploading a license may replace an
            existing key.
          </p>
          <label>
            Application
            <select
              aria-label="Application"
              .value=${this.licenseAppName}
              ?disabled=${!i||this.applicationPending}
              @change=${s=>{this.licenseAppName=s.currentTarget.value,this.licenseSelection=null}}
            >
              <option value="">Select an application</option>
              ${this.applications?.map(s=>c`<option value=${s.name}>${s.nice_name||s.name} (${s.name})</option>`)}
            </select>
          </label>
          ${a?c`<p>License status: ${a.license_status}</p>`:p}
          ${a&&(a.license_status==="Valid"||a.license_status==="Invalid")?this.licenseSelection===a?c`<p>
                      Remove the license for ${a.nice_name||a.name}?
                    </p>
                    <div class="actions">
                      <axis-button
                        variant="danger"
                        .busy=${this.applicationPending}
                        ?disabled=${!i||this.applicationPending}
                        @click=${()=>this.applyLicense(e)}
                        >Confirm license removal</axis-button
                      >
                      <axis-button
                        ?disabled=${this.applicationPending}
                        @click=${()=>this.licenseSelection=null}
                        >Cancel removal</axis-button
                      >
                    </div>`:c`<axis-button
                    variant="danger"
                    ?disabled=${!i||this.applicationPending}
                    @click=${()=>this.licenseSelection=a}
                    >Remove license</axis-button
                  >`:p}
          <div
            class="installation-drop"
            role="region"
            aria-label="License file drop area"
            ?data-dragging=${this.licenseDragging}
            @dragover=${s=>{s.preventDefault(),!(!i||this.applicationPending||this.licenseSelection)&&s.dataTransfer?.types.includes("Files")&&(s.dataTransfer.dropEffect="copy",this.licenseDragging=!0)}}
            @dragleave=${s=>{(!(s.relatedTarget instanceof Node)||!s.currentTarget.contains(s.relatedTarget))&&(this.licenseDragging=!1)}}
            @drop=${s=>{if(s.preventDefault(),this.licenseDragging=!1,!(!i||this.applicationPending||this.licenseSelection)){if(!s.dataTransfer?.files.length){this.licenseFile=null,this.licenseError="Drop one license file.";return}this.selectLicenseFile(s.dataTransfer.files)}}}
          >
            <p>Drag and drop a license file here</p>
            <span>or</span>
            <axis-button
              ?disabled=${!i||this.applicationPending||this.licenseSelection!==null}
              @click=${()=>this.renderRoot.querySelector(".license-file")?.click()}
              >Choose file</axis-button
            >
            <input
              class="license-file"
              type="file"
              accept=".xml"
              hidden
              ?disabled=${!i||this.applicationPending||this.licenseSelection!==null}
              @change=${s=>{let o=s.target;this.selectLicenseFile(o.files),o.value=""}}
            />
            ${this.licenseFile?c`<p>Selected: ${this.licenseFile.name}</p>`:p}
          </div>
          ${this.licenseError?c`<p class="error" role="alert">${this.licenseError}</p>`:p}
          ${this.applicationPending?c`<p role="status">${this.licenseSelection?"Removing license\u2026":"Uploading license file\u2026"}</p>`:p}
          <div class="actions">
            <axis-button
              variant="brand"
              .busy=${this.applicationPending}
              ?disabled=${!i||this.applicationPending||this.licenseSelection!==null||!this.licenseAppName||this.licenseFile===null}
              @click=${()=>this.uploadLicense(e)}
              >Confirm license upload</axis-button
            >
            <axis-button
              ?disabled=${this.applicationPending}
              @click=${this.closeLicense}
              >Cancel</axis-button
            >
          </div>
        </div>
      </dialog>
    `}async restart(e){if(!(this.restartPending||!this.restartConfirming)){this.restartPending=!0,this.restartMessage="",++this.operation,this.loading=null;try{await Ht(this.connection,e.serial),this.restartMessage="Restart requested.",this.restartFailed=!1}catch(i){this.restartMessage=i.message,this.restartFailed=!0}finally{this.invalidateDeviceViews(e.serial),this.selectedInterface=null,this.restartConfirming=!1,this.restartPending=!1}}}useCachedView(){++this.operation,this.loading=null,this.error=""}async browse(e,i,a="view"){let s=++this.operation;this.loading=a,this.error="";try{let o=await e();if(this.operation!==s)return;i(o)}catch(o){this.operation===s&&(this.error=o.message)}finally{this.operation===s&&(this.loading=null)}}renderSavedView(e,i){if(this.deviceView==="Health")return c`
        <axis-device-health
          .device=${e}
          .health=${this.viewData.health??null}
          .loading=${this.loading==="view"}
        ></axis-device-health>
      `;let{apis:a,interfaces:s,interfaceResults:o}=this.viewData,r=this.deviceView==="APIs"?a:this.selectedInterface===null?s:o?.get(this.selectedInterface);return c`
      <axis-card>
        <h3>${this.deviceView}</h3>
        ${this.deviceView==="Interfaces"?c`
                ${this.restartConfirming?c`<p>
                          Restart ${H(e)} (${e.serial})?
                        </p>
                        <div class="actions">
                          <axis-button
                            variant="brand"
                            .busy=${this.restartPending}
                            ?disabled=${this.restartPending||!i}
                            @click=${()=>this.restart(e)}
                            >Confirm restart</axis-button
                          >
                          <axis-button
                            ?disabled=${this.restartPending}
                            @click=${()=>this.restartConfirming=!1}
                            >Cancel</axis-button
                          >
                        </div>`:c`<axis-button
                        ?disabled=${!i||this.restartPending}
                        @click=${()=>{this.restartMessage="",this.restartConfirming=!0}}
                        >Restart device</axis-button
                      >`}
                ${this.restartMessage?c`<p role=${this.restartFailed?"alert":"status"}>
                        ${this.restartMessage}
                      </p>`:p}
              `:p}
        ${this.deviceView==="Interfaces"&&s?.length?c`<div class="actions">
                ${s.map(l=>c`
                    <axis-button
                      class=${l.name==="applications"?"application-trigger":""}
                      .pressed=${this.selectedInterface===l.name}
                      .busy=${this.loading==="interface"&&this.selectedInterface===l.name}
                      ?disabled=${!i||!l.supported||this.restartPending}
                      @click=${()=>this.showInterface(e.serial,l.name)}
                    >
                      ${l.name}
                    </axis-button>
                  `)}
              </div>`:p}
        ${this.deviceView==="APIs"&&a?.some(l=>l.doc_link)?c`
                <section aria-label="API documentation">
                  <h4>API documentation</h4>
                  <ul>
                    ${a.filter(l=>l.doc_link).map(l=>{let d=za(l.doc_link);return c`<li>
                          ${d?c`<a
                                  href=${d.href}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  >${l.name||l.id} — ${d.host}</a
                                >`:c`${l.name||l.id}: documentation link
                                unavailable`}
                        </li>`})}
                  </ul>
                </section>
              `:p}
        ${r!==void 0?c`<pre>${JSON.stringify(r,null,2)}</pre>`:p}
      </axis-card>
    `}async openSettings(e){this.connectionTest=null,this.connectionEdited=!1;let i={serial:e};this.settingsError="",this.settings=i;try{let a=await It(this.connection,e);if(this.settings!==i)return;this.settings={serial:e,value:a},await this.updateComplete,this.renderRoot.querySelector(".settings-form input")?.focus()}catch(a){this.settings===i&&(this.settingsError=a.message)}}async closeSettings(){this.settings=null,this.connectionTest=null,await this.updateComplete,this.renderRoot.querySelector(".settings-trigger")?.focus()}async submitSettings(e){e.preventDefault();let i=this.settings,a=e.currentTarget;if(!i?.value||this.settingsPending||this.connectionTest?.pending||!(a instanceof HTMLFormElement))return;let s=new FormData(a),o=ze(s,i.value.device);if(!(this.needsConnectionTest(o,i.value)&&!this.connectionVerified(o))){this.settingsError="",this.settingsPending=!0;try{let r=await Ot(this.connection,i.serial,{...o,alias:String(s.get("alias")??"")});if(this.settings!==i)return;this.devices=this.devices.map(l=>l.serial===i.serial?r.device:l),this.settingsPending=!1,this.closeSettings(),r.connection_changed&&(this.invalidateDeviceViews(i.serial),this.resetApplicationSupport(),this.selectedInterface=null,this.showDeviceView(i.serial,this.applicationsOpen?"Applications":this.deviceView))}catch(r){this.settings===i&&(this.settingsError=r.message)}finally{this.settings===i&&(this.settingsPending=!1)}}}renderSettings(){let e=this.settings?.value;return c`
      <axis-card>
        <h3>Device settings</h3>
        <p>These settings affect how Axis connects, not the device itself.</p>
        ${!e&&this.settingsError?c`<p class="error" role="alert">${this.settingsError}</p>`:p}
        ${e?this.renderSettingsForm(e):this.settingsError?c`<button type="button" @click=${this.closeSettings}>
                  Back
                </button>`:c`<p role="status">Loading settings…</p>`}
      </axis-card>
    `}async testConnection(e){let i=e.currentTarget,a=i instanceof HTMLElement?i.closest("form"):null;if(!a||this.connectionTest?.pending||!a.reportValidity())return;let s=this.registration,o=this.settings?.value?.device;if(!s&&!o||s&&this.registrationBlock(s))return;let r=ze(new FormData(a),o),l={pending:!0};this.connectionTest=l,this.settingsError="",this.saveError="";try{let d=o?await this.connection.callWS("device/test-connection",{...r,device:o.serial}):await this.connection.callWS("devices/test-connection",r);this.connectionTest===l&&(this.connectionTest={pending:!1,draft:r,message:`Connection successful (serial: ${d}).`})}catch(d){this.connectionTest===l&&(this.connectionTest={pending:!1,failed:!0,message:d.message})}}connectionVerified(e){let i=this.connectionTest?.draft;return i!==void 0&&JSON.stringify(i)===JSON.stringify(e)}needsConnectionTest(e,i){let{device:a,username:s}=i;return e.host.trim()!==a.host||e.port!==a.port||e.web_proto!==a.web_proto||e.verify_ssl!==a.verify_ssl||e.username.trim()!==s||e.password!==""}updateConnectionTest(e){if(this.connectionTest?.pending||!(e.target instanceof HTMLInputElement||e.target instanceof HTMLSelectElement)||e.target.name==="alias"||!(e.currentTarget instanceof HTMLFormElement)||e.type==="input"&&e.target instanceof HTMLSelectElement)return;this.connectionTest=null,this.saveError="",this.settingsError="";let i=this.settings?.value;i&&(this.connectionEdited=this.needsConnectionTest(ze(new FormData(e.currentTarget),i.device),i))}switchPortProtocol(e,i){let a=e.currentTarget;if(!(a instanceof HTMLSelectElement))return;let s=a.form?.elements.namedItem("port");if(!(s instanceof HTMLInputElement))return;let o=this.portDrafts.get(a)??{protocol:i,ports:new Map};o.ports.set(o.protocol,s.value),o.protocol=a.value,s.value=o.ports.get(o.protocol)??String(rt(o.protocol)),this.portDrafts.set(a,o)}renderSettingsForm(e,i=""){let a=!("device"in e),s=a?this.saving:this.settingsPending,o=this.connectionTest?.pending??!1,r=a?"Save device":"Save settings",l=this.connectionTest,d=(a||this.connectionEdited)&&!l?.draft,u=a?this.saveError:this.settingsError,g=a?e.name.trim()||e.host:H({...e.device,alias:""}),y=a?"https":e.device.web_proto,k=(a?0:e.device.port)||rt(y);return c`
      <form
        class="settings-form"
        method="post"
        @submit=${a?this.submitRegistration:this.submitSettings}
        @input=${this.updateConnectionTest}
        @change=${this.updateConnectionTest}
        @keydown=${C=>{C.key!=="Enter"||C.isComposing||!(C.target instanceof HTMLInputElement)||C.target.type==="checkbox"||(C.preventDefault(),!s&&!o&&!i&&!d&&C.currentTarget instanceof HTMLFormElement&&C.currentTarget.requestSubmit())}}
      >
        <fieldset ?disabled=${s||o}>
          <legend>General</legend>
          <label>
            Alias
            <input
              name="alias"
              .value=${a?"":e.device.alias}
              placeholder=${g}
            />
          </label>
        </fieldset>
        <fieldset ?disabled=${s||o}>
          <legend>Connection</legend>
          <label>
            Address
            <input
              name="host"
              .value=${a?e.host:e.device.host}
              ?readonly=${a}
              required
            />
          </label>
          <label>
            Port
            <input
              name="port"
              type="number"
              min="1"
              max="65535"
              .value=${String(k)}
              required
            />
          </label>
          <label>
            Username
            <input
              name="username"
              autocomplete="username"
              .value=${a?"":e.username}
              required
            />
          </label>
          <label>
            ${a?"Password":"New password"}
            <input
              name="password"
              type="password"
              autocomplete=${a?"current-password":"new-password"}
              placeholder=${a?p:"Keep current password"}
              ?required=${a}
            />
          </label>
        </fieldset>
        <fieldset ?disabled=${s||o}>
          <legend>Advanced</legend>
          <label>
            Protocol
            <select
              name="web_proto"
              @change=${C=>this.switchPortProtocol(C,y)}
            >
              <option value="https" ?selected=${y==="https"}>
                HTTPS
              </option>
              <option value="http" ?selected=${y==="http"}>
                HTTP
              </option>
            </select>
          </label>
          <label class="certificate">
            <input
              name="verify_ssl"
              type="checkbox"
              .checked=${!a&&e.device.verify_ssl}
            />
            Verify HTTPS certificates
          </label>
          ${a?c`<small class="warning">
                  Turning verification off allows self-signed certificates but
                  skips certificate checks. HTTP is not encrypted. Verify the
                  address and only continue if you trust the device and network.
                </small>`:c`<small>
                  Use HTTPS with certificate verification when possible. HTTP is
                  not encrypted.
                </small>`}
        </fieldset>
        <div class="actions">
          <axis-button
            type="submit"
            variant=${u?"danger":"brand"}
            .busy=${s}
            ?disabled=${s||o||d||!!i}
            title=${i||u||(d?"Test the connection before saving.":"")}
          >
            ${r}
          </axis-button>
          <axis-button
            type="button"
            variant=${l?.failed?"danger":l?.draft?"success":"neutral"}
            .busy=${o}
            ?disabled=${s||o||!!i}
            title=${i||l?.message||""}
            @click=${this.testConnection}
          >
            Test connection
          </axis-button>
          <axis-button
            type="button"
            ?disabled=${s}
            @click=${a?this.dismissDevice:this.closeSettings}
          >
            Cancel
          </axis-button>
        </div>
        <div class="form-status" role="status">
          ${i||(l?.draft?l.message:"")}
        </div>
        <div class="form-status" role="alert">
          ${u||(l?.failed?l.message:"")}
        </div>
      </form>
    `}async openServerSettings(){this.serverSettingsOpen=!0,this.closeFolderBrowser(),this.serverSettings=null,this.acapCatalog=null,this.acapCatalogError="",this.serverError="",this.serverPending=!0;try{let e=await this.connection.callWS("server/settings",{});if(!this.serverSettingsOpen)return;this.serverSettings=e,this.acapFolder=e.acap_folder??"",this.serverAutomatic=e.selected===null,this.serverSelection=e.selected??e.interfaces.filter(i=>i.up&&i.addresses.length).map(i=>i.name),e.acap_folder&&this.loadAcapCatalog()}catch(e){this.serverSettingsOpen&&(this.serverError=e.message)}finally{this.serverPending=!1}}closeFolderBrowser(){++this.folderBrowserRequest,this.folderBrowserOpen=!1,this.folderBrowser=null,this.folderBrowserPending=!1,this.folderBrowserError=""}async browseFolders(e){let i=++this.folderBrowserRequest;this.folderBrowserOpen=!0,this.folderBrowserPending=!0,this.folderBrowserError="";try{let a=await this.connection.callWS("server/browse-folders",{path:e});i===this.folderBrowserRequest&&this.serverSettingsOpen&&(this.folderBrowser=a)}catch(a){i===this.folderBrowserRequest&&this.serverSettingsOpen&&(this.folderBrowserError=a.message)}finally{i===this.folderBrowserRequest&&(this.folderBrowserPending=!1)}}async loadAcapCatalog(e=!1){this.acapCatalogError="";try{let i=await this.connection.callWS(e?"acap/scan":"acap/catalog",{});this.serverSettingsOpen&&(this.acapCatalog=i,this.acapCatalogError=i.error)}catch(i){this.serverSettingsOpen&&(this.acapCatalogError=i.message)}}async saveServerSettings(e){if(e.preventDefault(),!this.folderBrowserOpen){if(!this.serverAutomatic&&!this.serverSelection.length){this.serverError="Select at least one interface, or use automatic discovery.";return}this.serverPending=!0,this.serverError="";try{await this.connection.callWS("server/configure",{interfaces:this.serverAutomatic?null:this.serverSelection,acap_folder:this.acapFolder.trim()||null}),this.serverPending=!1,this.dismissDevice()}catch(i){this.serverSettingsOpen&&(this.serverError=i.message)}finally{this.serverPending=!1}}}renderServerSettings(){let e=this.serverSettings;return c`
      <axis-card>
        <h3>Discovery network interfaces</h3>
        <p>Changes apply to the next web discovery scan.</p>
        ${this.serverError?c`<p class="error" role="alert">${this.serverError}</p>`:p}
        ${e?c`
                <form @submit=${this.saveServerSettings}>
                  <fieldset
                    class="server-interfaces"
                    ?disabled=${this.serverPending}
                  >
                    <label>
                      <input
                        type="radio"
                        name="mode"
                        .checked=${this.serverAutomatic}
                        @change=${()=>this.serverAutomatic=!0}
                      />
                      Use all interfaces automatically
                    </label>
                    <label>
                      <input
                        type="radio"
                        name="mode"
                        .checked=${!this.serverAutomatic}
                        @change=${()=>this.serverAutomatic=!1}
                      />
                      Use selected interfaces
                    </label>
                    ${e.interfaces.map(i=>c`
                        <label>
                          <input
                            type="checkbox"
                            .checked=${this.serverSelection.includes(i.name)}
                            ?disabled=${this.serverAutomatic}
                            @change=${a=>{let s=a.target.checked;this.serverSelection=s?[...this.serverSelection,i.name]:this.serverSelection.filter(o=>o!==i.name)}}
                          />
                          <span>
                            ${i.label}${i.label!==i.name?` (${i.name})`:""}
                            <span class="server-interface-detail">
                              —
                              ${i.up===!1?"Down":i.up===null?"Unavailable":i.addresses.join(", ")||"No IPv4 address"}
                            </span>
                          </span>
                        </label>
                      `)}
                  </fieldset>
                  <h3>ACAP package folder</h3>
                  <p>
                    Browse or enter an absolute folder path on the server.
                    Packages are scanned automatically; updates always require
                    confirmation.
                  </p>
                  <label>
                    Server folder
                    <input
                      type="text"
                      .value=${this.acapFolder}
                      ?disabled=${this.serverPending}
                      @input=${i=>{this.acapFolder=i.currentTarget.value}}
                    />
                  </label>
                  <axis-button
                    type="button"
                    ?disabled=${this.serverPending||this.folderBrowserOpen}
                    @click=${()=>this.browseFolders(this.acapFolder.trim()||null)}
                    >Browse folders</axis-button
                  >
                  ${this.folderBrowserOpen?c`
                          <section
                            class="folder-browser"
                            aria-label="Browse server folders"
                          >
                            <h4>Browse server folders</h4>
                            ${this.folderBrowser?c`<p>Current folder: ${this.folderBrowser.path}</p>`:p}
                            ${this.folderBrowserPending?c`<p role="status">Loading folders…</p>`:p}
                            ${this.folderBrowserError?c`<p class="error" role="alert">${this.folderBrowserError}</p>`:p}
                            <div class="actions">
                              <axis-button
                                type="button"
                                ?disabled=${this.folderBrowserPending}
                                @click=${()=>this.browseFolders(null)}
                                >Home</axis-button
                              >
                              <axis-button
                                type="button"
                                ?disabled=${this.folderBrowserPending||!this.folderBrowser?.parent}
                                @click=${()=>this.folderBrowser?.parent&&this.browseFolders(this.folderBrowser.parent)}
                                >Parent folder</axis-button
                              >
                            </div>
                            <div class="folder-list">
                              ${this.folderBrowser?.directories.map(i=>c`
                                  <axis-button
                                    type="button"
                                    ?disabled=${this.folderBrowserPending}
                                    @click=${()=>this.browseFolders(i.path)}
                                    >Open ${i.name}</axis-button
                                  >
                                `)}
                            </div>
                            ${this.folderBrowser&&!this.folderBrowserPending&&!this.folderBrowser.directories.length?c`<p>No subfolders.</p>`:p}
                            <div class="actions">
                              <axis-button
                                type="button"
                                variant="brand"
                                ?disabled=${this.folderBrowserPending||!this.folderBrowser}
                                @click=${()=>{this.folderBrowser&&(this.acapFolder=this.folderBrowser.path),this.closeFolderBrowser()}}
                                >Select this folder</axis-button
                              >
                              <axis-button
                                type="button"
                                @click=${this.closeFolderBrowser}
                                >Cancel browsing</axis-button
                              >
                            </div>
                          </section>
                        `:p}
                  ${e.acap_folder?c`
                          <p>Catalog for ${e.acap_folder}</p>
                          <axis-button
                            type="button"
                            ?disabled=${this.serverPending}
                            @click=${()=>this.loadAcapCatalog(!0)}
                            >Scan ACAP folder</axis-button
                          >
                          ${this.acapCatalogError?c`<p role="alert">${this.acapCatalogError}</p>`:p}
                          ${this.acapCatalog?.errors.map(i=>c`<p role="alert">${i.filename}: ${i.message}</p>`)}
                          ${this.acapCatalog?c`<p>
                                    ${this.acapCatalog.packages.length} packages
                                    found.
                                  </p>
                                  ${this.acapCatalog.packages.map(i=>c`<p>
                                        ${i.friendly_name||i.name||i.filename}
                                        (${i.name||"Unknown"}), version
                                        ${i.version||"Unknown"},
                                        architecture
                                        ${i.architecture||"Unknown"},
                                        vendor ${i.vendor||"Unknown"},
                                        vendor ID
                                        ${i.vendor_id||"Unknown"}, SDK
                                        ${i.sdk||"Unknown"}, size
                                        ${i.size} bytes, AXIS OS
                                        ${i.os_ranges.length?i.os_ranges.map(([a,s])=>`${a||"?"}\u2013${s||"?"}`).join(", "):"Unknown"},
                                        signature
                                        ${i.signature==="present_unverified"?"present, not verified":i.signature==="not_detected"?"not detected":"unknown"}.
                                        The device must verify the signature,
                                        vendor ID, and other installation
                                        requirements.
                                      </p>`)}`:p}
                        `:p}
                  <div class="actions">
                    <axis-button
                      type="submit"
                      variant="brand"
                      .busy=${this.serverPending}
                      ?disabled=${this.serverPending||this.folderBrowserOpen}
                      >Save settings</axis-button
                    >
                    <axis-button
                      type="button"
                      ?disabled=${this.serverPending}
                      @click=${this.dismissDevice}
                      >Cancel</axis-button
                    >
                  </div>
                </form>
              `:p}
      </axis-card>
    `}renderConnectionStatus(e){return c`
      <span class="connection-status" data-state=${this.status}>
        <span role="status">${e}</span>
      </span>
    `}render(){let e=this.devices.find(r=>r.serial===this.selected),i=this.status==="connected",a=Pa[this.status],s=this.serverSettingsOpen||this.registration!==null||this.selected!=="",o=this.error?c`<p class="error" role="alert">${this.error}</p>`:p;return c`
      <main>
        <header class="app-heading">
          <div class="connection-heading" title=${a}>
            <h1 tabindex="-1">Axis devices</h1>
            ${this.renderConnectionStatus(a)}
          </div>
          <button
            type="button"
            class="server-settings-trigger"
            ?disabled=${!i||this.saving}
            @click=${this.openServerSettings}
          >
            Server settings
          </button>
        </header>
        ${s?p:o}
        <axis-device-list
          .devices=${this.devices}
          .discovery=${this.discovery}
          .selected=${this.selected}
          .connected=${i&&!this.saving}
          .warning=${this.discoveryWarning}
          @axis-scan=${this.scanLocalNetwork}
          @axis-select=${r=>{this.registration=null,this.showDeviceView(r.detail,"Health")}}
          @axis-register=${r=>this.openRegistration(r.detail)}
        >
        </axis-device-list>
      </main>
      <dialog
        aria-labelledby="device-dialog-title"
        @pointerdown=${r=>{let l=r.currentTarget;if(this.backdropPressed=!1,r.target===l&&l instanceof HTMLDialogElement){let d=l.getBoundingClientRect();this.backdropPressed=r.clientX<d.left||r.clientX>=d.right||r.clientY<d.top||r.clientY>=d.bottom}}}
        @pointercancel=${()=>{this.backdropPressed=!1}}
        @click=${r=>{let l=r.currentTarget;if(this.backdropPressed&&r.target===l&&l instanceof HTMLDialogElement){let d=l.getBoundingClientRect();(r.clientX<d.left||r.clientX>=d.right||r.clientY<d.top||r.clientY>=d.bottom)&&this.dismissDevice(r)}this.backdropPressed=!1}}
        @cancel=${r=>{if(this.settings){r.preventDefault(),this.settingsPending||this.closeSettings();return}if(this.applicationsOpen){r.preventDefault(),this.closeApplications();return}this.dismissDevice(r)}}
      >
        <div class="dialog-header">
          <header class="dialog-heading">
            <h2 id="device-dialog-title">
              ${this.serverSettingsOpen?"Server settings":this.registration?this.registration.name.trim()||this.registration.host:e?H(e):"Device details"}
            </h2>
            <div class="dialog-controls">
              ${e?c`<button
                      type="button"
                      class="settings-trigger"
                      aria-pressed=${String(this.settings!==null)}
                      ?disabled=${!i||this.settingsPending||this.restartPending||this.applicationPending}
                      @click=${()=>this.settings?this.closeSettings():this.openSettings(e.serial)}
                    >
                      Settings
                    </button>`:p}
              <button
                type="button"
                autofocus
                ?disabled=${this.saving||this.settingsPending||this.serverPending||this.restartPending||this.applicationPending}
                @click=${this.dismissDevice}
              >
                Close
              </button>
            </div>
          </header>
          ${e?c`<nav
                  class="actions device-views"
                  aria-label="Device views"
                >
                  ${_a.map(r=>c`
                      <axis-button
                        class=${!this.settings&&(r==="Applications"?this.applicationsOpen:!this.applicationsOpen&&this.deviceView===r)?"active":""}
                        variant="neutral"
                        .pressed=${!this.settings&&(r==="Applications"?this.applicationsOpen:!this.applicationsOpen&&this.deviceView===r)}
                        .busy=${r==="Applications"?this.applicationsOpen&&this.applications===null&&(this.applicationLoading||this.applicationSupportPending!==null):this.loading==="view"&&this.deviceView===r}
                        ?disabled=${!i||this.settingsPending||this.restartPending||this.applicationPending}
                        @click=${()=>{let l=!this.settings&&(r==="Applications"?this.applicationsOpen:!this.applicationsOpen&&this.deviceView===r);this.settings=null,this.connectionTest=null,this.restartConfirming=!1,this.showDeviceView(e.serial,r,l)}}
                        >${r}</axis-button
                      >
                    `)}
                </nav>`:p}
        </div>
        <div class="panels dialog-content">
          ${s?o:p}
          ${this.serverSettingsOpen?this.renderServerSettings():p}
          ${this.registration?this.renderRegistration(this.registration):p}
          ${this.settings?this.renderSettings():e&&this.applicationsOpen?this.renderApplications(e,i):e?this.renderSavedView(e,i):p}
        </div>
      </dialog>
      ${e&&this.applicationsOpen?this.renderInstallationDialog(e,i):p}
      ${e&&this.applicationsOpen?this.renderInstallDetail(i):p}
      ${e&&this.applicationsOpen?this.renderApplicationDialog(e,i):p}
      ${e&&this.applicationsOpen?this.renderUpdateDialog(e,i):p}
      ${e&&this.applicationsOpen?this.renderLicenseDialog(e,i):p}
    `}};customElements.define("axis-app",lt);
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
